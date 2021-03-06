#include "stemmedfileinmemoryparser.h"

#include <locale>
#include <algorithm>
#include <set>
#include <cmath>
#include <cfloat>
#include <fstream>
#include <functional>
#include <iostream>
#include <string>
#include <sstream>
#include <cstdlib>
#include <thread>
#include <chrono>

//#include <QMap>
/// We don't care for DBL_MIN, so quantization has to be at 2*DBL_MIN,
/// so smallest values have to be 4*DBL_MIN, so minimal value has to be bigger
/// then that.
double StemmedFileInMemoryParser::MinimalValueLowerBound = DBL_MIN * 5;

StemmedFileInMemoryParser::StemmedFileInMemoryParser():
    _nextCoord(1), // R needs indecies starting from 1
    minimalValue(DBL_MAX)
{
  this->_max.longitude = DBL_MIN;
  this->_max.latitude = DBL_MIN;
  this->_max.countOfNonZero = DBL_MIN;
  this->_max.distanceFromMax = DBL_MIN;
  this->_max.distanceFromMean = DBL_MIN;
  this->_max.distanceFromZero = DBL_MIN;
  this->_min.longitude = DBL_MAX;
  this->_min.latitude = DBL_MAX;
  this->_min.countOfNonZero = DBL_MAX;
  this->_min.distanceFromMax = DBL_MAX;
  this->_min.distanceFromMean = DBL_MAX;
  this->_min.distanceFromZero = DBL_MAX;
}

StemmedFileInMemoryParser::~StemmedFileInMemoryParser()
{
    for(auto &pair : this->_wordsCountPerDocument)
    {
        delete pair.second;
        pair.second = 0;
    }

    for(auto & map : this->tfIdfResults)
    {
        delete map.second;
        map.second = 0;
    }
}

bool StemmedFileInMemoryParser::loadData(const char* stemmedFile, const char* stopWordFile)
{
    std::cout << __FUNCTION__ << std::endl;

    std::ifstream stopWordFin(stopWordFile, std::ios::in);
    std::set<std::string> stopWords;
    bool enteredStopWords = false;
    if(stopWordFin.is_open())
    {
        std::cout << "Using stop word list" << std::endl;
        while(!stopWordFin.eof())
        {
	    enteredStopWords = true;
            std::string line;
            std::getline(stopWordFin, line);
            std::string stopWord = line.substr(0,line.find_first_of(' '));
            // remove SPDB data from stopwords
            if (stopWord.find("spdb") == 0)
            {
                continue;
            }
            stopWords.insert(stopWord); // skip everything after first space
        }
        std::cout << "Stop words list size: " << stopWords.size() << std::endl;
    }

    std::ifstream in(stemmedFile, std::ios::in);
    if(!in.is_open())
        return false;
    unsigned docNumber = 0;
    while(!in.eof())
    {
        std::string line;
        std::getline(in, line);
        std::stringstream inner(std::ios::in);
        inner.str(line);
        inner.seekg(0, std::ios_base::beg);
        unsigned int lineLen = 0;
        std::unordered_map<size_t, unsigned int>* doc = new std::unordered_map<size_t, unsigned int>();
        std::unordered_map<size_t, bool> alreadyInserted;

        // first word is a fileId, which should not be processed
        std::string fileId;
	inner >> fileId;

        while(!inner.eof())
        {
            std::string word;
            inner >> word;
            word.erase(std::remove_if(word.begin(), word.end(), ::isspace), word.end());
            ++lineLen;
            if ( stopWords.find(word) != stopWords.end() )
            {
                // skip stopword
                //std::cout << "Skipping " << word << std::endl;
                continue;
            }

            if(enteredStopWords && word.find("spdbcoordlong") == 0)
	    {
	      std::string longitudeStr = word.substr(13);
	      if (this->_geoPerDoc.count(docNumber) > 0)
		this->_geoPerDoc[docNumber].first = atof(longitudeStr.c_str());
	      else
	        this->_geoPerDoc.insert({docNumber, std::make_pair<double, double>(atof(longitudeStr.c_str()), 0.0)});
	    }
	    if(enteredStopWords && word.find("spdbcoordlat") == 0)
	    {
	      std::string latitudeStr = word.substr(13);
	      if (this->_geoPerDoc.count(docNumber) > 0)
		this->_geoPerDoc[docNumber].second = atof(latitudeStr.c_str());
	      else
	        this->_geoPerDoc.insert({docNumber, std::make_pair<double, double>(0.0, atof(latitudeStr.c_str()))});
	    }
	    
            size_t hash = this->hash_fn(word);
            if(this->_wordsToCoords.count(hash) == 0)
            {
                this->_wordsToCoords.insert({hash, _nextCoord});
                this->_dictionary[_nextCoord] = std::pair<std::string, unsigned int>(word,1);
                _nextCoord++;
            }
            else
            {
                this->_dictionary[this->_wordsToCoords[hash]].second++; // increase count
            }

            if(doc->count(hash) == 0)
                doc->insert({hash, 1});
            else
                (*doc)[hash] += 1;
            if(this->_globalWordsCount.count(hash) > 0)
                this->_globalWordsCount.insert({hash, 1});
            else
                this->_globalWordsCount[hash] += 1;
            if(alreadyInserted.count(hash) == 0)
            {
                alreadyInserted.insert({hash, true});
                if(this->_numberOfDocumentsWithGivenWords.count(hash) == 0)
                    this->_numberOfDocumentsWithGivenWords.insert({hash, 1});
                else
                    this->_numberOfDocumentsWithGivenWords[hash] += 1;
            }
        }
        
        if (fileId.size() > 2)
	{
	  unsigned docIndex = docNumber++;
          this->_docName.push_back({docIndex, fileId});
          this->_docsLens.insert({docIndex, lineLen});
          this->_wordsCountPerDocument.insert({docIndex, doc});
	}
    }
    in.close();
    return true;
}

double StemmedFileInMemoryParser::tfidf(size_t word, unsigned int docIndex)
{
    return tf(word, docIndex) * idf(word);
}

double StemmedFileInMemoryParser::tf(size_t word, unsigned int docIndex)
{
    return (double)(*_wordsCountPerDocument[docIndex])[word] /
           (double)_docsLens[docIndex];
}

double StemmedFileInMemoryParser::idf(size_t word)
{
    return log((double)_wordsCountPerDocument.size() /
                (double)_numberOfDocumentsWithGivenWords[word]);
}

void StemmedFileInMemoryParser::countTfidf()
{
    std::cout << __FUNCTION__ << std::endl;
    for(auto wordPerDocPair : this->_wordsCountPerDocument)
    { // for all docs
        std::unordered_map<unsigned, double>* map = new std::unordered_map<unsigned, double>();
        for(auto word : *(wordPerDocPair.second))
        { // for all words in doc - counting tfidf
            double tfidfOfWord = this->tfidf(word.first, wordPerDocPair.first);
            if(tfidfOfWord < this->minimalValue && tfidfOfWord > MinimalValueLowerBound)
                this->minimalValue = tfidfOfWord;
            unsigned coordsIndex = this->_wordsToCoords[word.first];
            map->insert({coordsIndex, tfidfOfWord});
        }
        this->tfIdfResults[wordPerDocPair.first] = map;
    }
    this->quant = this->minimalValue / 4;
}

void StemmedFileInMemoryParser::createStopWordList(double thresholdUpper,
                                                   double thresholdBottom,
                                                   unsigned int stopWordCountBottom,
                                                   const char* stopWordFile)
{
    std::cout << __FUNCTION__ << " thresholdUpper:"  << thresholdUpper <<
                                 " thresholdBottom:" << thresholdBottom <<
                                 " stopWordCountBottom:" << stopWordCountBottom << std::endl;

    // list stop words
    std::set<unsigned int> toRemove;
    for( auto & results : this->tfIdfResults )
    {
        for(auto & pair : *results.second)
        {
            if( pair.second < thresholdBottom ||
                pair.second > thresholdUpper )
            {
                toRemove.insert(pair.first);
            }

            if ( this->_dictionary[pair.first].second < stopWordCountBottom )
                 // TODO needed? this->_dictionary[pair.first].second > 100 )
            {
                toRemove.insert(pair.first);
            }
        }
    }

    // save to remove words
    std::ofstream outDict(stopWordFile, std::ios::trunc | std::ios::out);
    if(outDict.is_open())
    {
        for(auto & entry : toRemove)
        {
            outDict << this->_dictionary[entry].first << " : " << this->_dictionary[entry].second << std::endl;
        }

        //outDict << std::ends;
        outDict.flush();
        outDict.close();
    }
}

bool StemmedFileInMemoryParser::storeTfidfInFile(const char* tfidfFileName, const char* dictFileName)
{
    std::cout << __FUNCTION__ << std::endl;
    std::ofstream out(tfidfFileName, std::ios::trunc | std::ios::out);
    if(!out.is_open())
        return false;
    //out << _wordsCountPerDocument.size() << " " << _nextCoord << " " << this->quant << std::endl; // header format: <number of vectors> <number of dimensions> <quantization value>
    for(auto docName : this->_docName)
    { // for all docs
        out << docName.second << ' '; // add fileId at the beginning
        
        auto map = this->tfIdfResults[docName.first];
        for(auto pair : *map)
        { // for all words in doc - counting tfidf
            if(pair.second < DBL_MIN)
                pair.second = this->minimalValue / 2;
            out << pair.first << ':' << pair.second << ' ';
        }
        out << std::endl;
    }
    //out << std::ends;
    out.flush();
    out.close();

    // save dictionary
    std::ofstream outDict(dictFileName, std::ios::trunc | std::ios::out);
    if(outDict.is_open())
    {
        for(auto & entry : this->_dictionary)
        {
            outDict << entry.first << " : " << entry.second.first << " : " << entry.second.second << std::endl;
        }

        //outDict << std::ends;
        outDict.flush();
        outDict.close();
    }

    return true;
}

double addCoordsForEuclidean(
  const std::unordered_map<unsigned int, double>& two,
  const std::unordered_map<unsigned int, double>& one, 
  unsigned int index)
{
  double result = 0.0;
  if(one.count(index) > 0 && two.count(index) > 0)
      result += pow(one.at(index) - two.at(index), 2.0);
    else if(one.count(index) > 0)
      result += pow(one.at(index), 2.0);
    else if(two.count(index) > 0)
      result += pow(two.at(index), 2.0);
    
    return result;
}

std::pair<double, double> euclideanDistanceFromZeroAndMean(
  const std::unordered_map<unsigned int, double>& mean,
  const std::unordered_map<unsigned int, double>& zero,
  const std::unordered_map<unsigned int, double>& one,
  const unsigned int numDims)
{
  std::pair<double, double> result;
  for(unsigned int i=0; i<numDims; ++i)
  {
    result.first = addCoordsForEuclidean(mean, one, i);
    result.second = addCoordsForEuclidean(one, zero, i);
  }
  
  result.first = sqrt(result.first);
  result.second = sqrt(result.second);
  return result;
}

double euclideanDistance(
  const std::unordered_map<unsigned int, double>& two,
  const std::unordered_map<unsigned int, double>& one, 
  unsigned int numDims)
{
  double result = 0.0;
  for(unsigned int i=0; i<numDims; ++i)
  {
    result = addCoordsForEuclidean(one, two, i);
  }
  
  return sqrt(result);
}

double getMax(double value, double currentMax)
{
  return value > currentMax ? value : currentMax;
}

double getMin(double value, double currentMin)
{
  return value < currentMin ? value : currentMin;
}

double safeNumericNormalization(double valueToNormalize, double max, double min)
{
  return ((valueToNormalize * 32) - (min * 32)) / max;
}

void StemmedFileInMemoryParser::normalizeFeatures()
{
  const unsigned int numPoints = this->tfIdfResults.size();
  bool isGeoPresent = this->_geoPerDoc.size() > 0;
  for (unsigned int pIndex = 0; pIndex < numPoints; ++pIndex)
  {
    Feature &f = this->_dataFeatures[pIndex];
    if (isGeoPresent)
    {
      this->_dataFeatures[pIndex].longitude = safeNumericNormalization(f.longitude, this->_max.longitude, this->_min.longitude);
      this->_dataFeatures[pIndex].latitude = safeNumericNormalization(f.latitude, this->_max.latitude, this->_min.latitude);
    }
    
    this->_dataFeatures[pIndex].countOfNonZero = safeNumericNormalization(f.countOfNonZero, this->_max.countOfNonZero, this->_min.countOfNonZero);
    this->_dataFeatures[pIndex].distanceFromMax = safeNumericNormalization(f.distanceFromMax, this->_max.distanceFromMax, this->_min.distanceFromMax);
    this->_dataFeatures[pIndex].distanceFromMean = safeNumericNormalization(f.distanceFromMean, this->_max.distanceFromMean, this->_min.distanceFromMean);
    this->_dataFeatures[pIndex].distanceFromZero = safeNumericNormalization(f.distanceFromZero, this->_max.distanceFromZero, this->_min.distanceFromZero);
  }
}


void StemmedFileInMemoryParser::countFeatures()
{
  // find mean point
  std::unordered_map<unsigned int, double> meanPoint;
  std::unordered_map<unsigned int, double> zeroPoint; // doesn't need initialiation, zero coords are empty indies.
  unsigned int maxPointIndex = -1;
  const unsigned int numDim = this->_nextCoord;
  double maxDistance = 0.0;
  for(auto point : this->tfIdfResults)
  {
    for(auto coords : *(point.second))
    {
      if (meanPoint.count(coords.first) > 0)
	meanPoint[coords.first] += coords.second;
      else
	meanPoint.insert({coords.first, coords.second});
    }
  }
  
  const unsigned int numPoints = this->tfIdfResults.size();
  for(unsigned int i =0; i<numDim; ++i)
  {
    if(meanPoint.count(i) > 0)
    {
      meanPoint[i] = meanPoint[i] / numPoints; // finishing up with mean point
    }
  }
  
  bool isGeoPresent = this->_geoPerDoc.size() > 0;
  
  for(unsigned int pIndex = 0; pIndex < numPoints; ++pIndex)
  {
    Feature f;
    if (isGeoPresent)
    {
      f.longitude = this->_geoPerDoc[pIndex].first;
      f.latitude = this->_geoPerDoc[pIndex].second;
      this->_max.latitude = getMax(f.latitude, this->_max.latitude);
      this->_min.latitude = getMin(f.latitude, this->_min.latitude);
      this->_max.longitude = getMax(f.longitude, this->_max.longitude);
      this->_min.longitude = getMin(f.longitude, this->_min.longitude);
    }
    std::unordered_map<unsigned int, double>* point = this->tfIdfResults[pIndex];
    f.countOfNonZero = (double)point->size();
    std::pair<double, double> meanAndZeroDist = euclideanDistanceFromZeroAndMean(meanPoint, zeroPoint, *point, numDim);
    f.distanceFromMean = meanAndZeroDist.first;
    f.distanceFromZero = meanAndZeroDist.second;
    if(f.distanceFromZero > maxDistance)
      maxPointIndex = pIndex;
    this->_dataFeatures.insert({pIndex, f});
    this->_max.countOfNonZero = getMax(f.countOfNonZero, this->_max.countOfNonZero);
    this->_min.countOfNonZero = getMin(f.countOfNonZero, this->_min.countOfNonZero);
    this->_max.distanceFromMean = getMax(f.distanceFromMean, this->_max.distanceFromMean);
    this->_min.distanceFromMean = getMin(f.distanceFromMean, this->_min.distanceFromMean);
    this->_max.distanceFromZero = getMax(f.distanceFromZero, this->_max.distanceFromZero);
    this->_min.distanceFromZero = getMin(f.distanceFromZero, this->_min.distanceFromZero);
  }
  
  std::unordered_map<unsigned int, double>* maxPoint =  this->tfIdfResults[maxPointIndex];
  for (unsigned int pIndex = 0; pIndex < numPoints; ++pIndex)
  {
    if(pIndex != maxPointIndex)
    {
      this->_dataFeatures[pIndex].distanceFromMax = euclideanDistance(*(this->tfIdfResults[pIndex]), *maxPoint, numDim);
    }
    else 
    {
      this->_dataFeatures[pIndex].distanceFromMax = 0.0;
    }
    
    this->_max.distanceFromMax = getMax(this->_dataFeatures[pIndex].distanceFromMax, this->_max.distanceFromMax);
    this->_min.distanceFromMax = getMin(this->_dataFeatures[pIndex].distanceFromMax, this->_min.distanceFromMax);
  }

  this->normalizeFeatures();
}

void StemmedFileInMemoryParser::storeFeatures(const char* featureFile)
{
    std::cout << __FUNCTION__ << std::endl;
    std::ofstream out(featureFile, std::ios::trunc | std::ios::out);
    if(!out.is_open())
    {
      std::cout << "Cannot create features file" << std::endl;
      return;
    }
    
    std::cout << "DocName size: " << this->_docName.size() << std::endl;
    std::cout << "Data features size: " << this->_dataFeatures.size() << std::endl;
    //out << _wordsCountPerDocument.size() << " " << _nextCoord << " " << this->quant << std::endl; // header format: <number of vectors> <number of dimensions> <quantization value>
    for(auto docName : this->_docName)
    { // for all docs
        Feature f = this->_dataFeatures[docName.first];
        out << docName.second << ' ' << f.countOfNonZero << " " << f.distanceFromMax << " " << f.distanceFromMean << " "
	  << f.distanceFromZero << " " << f.longitude << " " << f.latitude << std::endl;
    }
    //out << std::ends;
    out.flush();
    out.close();
    std::cout << "after close store features" << std::endl;
}


void CountCoordinateSimilarity( const char* parsedCoordsFile,
                                const char* similarityCoordsFile )
{
    std::cout << __FUNCTION__ << std::endl;

    std::ifstream in1(parsedCoordsFile, std::ios::in);
    if(!in1.is_open())
        return;

    int rowCount=0;
    while(!in1.eof())
    {
        std::string line;
        std::getline(in1, line);
        rowCount++;
    }
    in1.close();

    std::vector<int> longitudeV(rowCount, 0x00);
    std::vector<int> latitudeV(rowCount, 0x00);
    std::vector<std::string> fileIdV(rowCount, "");

    std::ifstream in(parsedCoordsFile, std::ios::in);
    if(!in.is_open())
        return;
    int rowIndex = 0;
    while(!in.eof())
    {
        std::string line;
        std::getline(in, line);
        std::stringstream inner(std::ios::in);
        inner.str(line);
        inner.seekg(0, std::ios_base::beg);

        // first word is a fileId
        std::string fileId;
	inner >> fileId;
        fileIdV[rowIndex] = fileId;

        std::string longitude, latitude;
        inner >> longitude;
        inner >> latitude;

        longitudeV[rowIndex] = atoi(longitude.c_str());
        latitudeV[rowIndex] = atoi(latitude.c_str());

        rowIndex++;
    }
    in.close();

    // rowId to columnId-distance
    std::vector<std::vector<float>> distanceV(rowCount, std::vector<float>(rowCount,0));

    auto a = [&](int start, int end)
    {
        std::cout << "thread start:" << start << " end:" << end << std::endl;
        // iterate rows and columns of distance matrix
        for (int r = start; r < end; r++)
        {
            if (start == 0)
            {
                std::cout << "\r" << 6*r << "/"<< rowCount << " completed.       " << std::flush;
            }

            for (int c = 0; c < rowCount-r; c++)
            {
                const int x = longitudeV[r] - longitudeV[c];
                const int y = latitudeV[r] - latitudeV[c];

                // calculating Euclidean distance
                float distance = pow(x, 2) + pow(y, 2);
	        distance = sqrt(distance);

                distanceV[r][c] = distance;
            
                //std::cout << "distance " << r << "(" << longitudeV[r] << " " << latitudeV[r] << ") " << ":" << c << "(" << longitudeV[c] << " " << latitudeV[c] << ") " << distance << std::endl;
            }
        }
    };
   
    std::thread second(a, 1*(rowCount/6)+1, 2*(rowCount/6));
    std::this_thread::sleep_for(std::chrono::milliseconds(400));
    std::thread third(a,  2*(rowCount/6)+1, 3*(rowCount/6));
    std::this_thread::sleep_for(std::chrono::milliseconds(400));
    std::thread fourth(a, 3*(rowCount/6)+1, 4*(rowCount/6));
    std::this_thread::sleep_for(std::chrono::milliseconds(400));
    std::thread fifth(a,  4*(rowCount/6)+1, 5*(rowCount/6));
    std::this_thread::sleep_for(std::chrono::milliseconds(400));
    std::thread sixth(a,  5*(rowCount/6)+1,    rowCount);
    std::this_thread::sleep_for(std::chrono::milliseconds(400));
    std::thread first(a,  0,                   rowCount/6);

    first.join();
    second.join();
    third.join();
    fourth.join();
    fifth.join();
    sixth.join();

    std::cout << std::endl << "Find max distance..." << std::endl;
    int maxElement = 0;
    int rIndex = 0;
    for ( auto & entry : distanceV )
    {
	const int cMaxIndex = std::distance(entry.begin(), std::max_element(entry.begin(), entry.end()));
        maxElement = (distanceV[rIndex][cMaxIndex] > maxElement ? distanceV[rIndex][cMaxIndex] : maxElement);
        //std::cout << "maxElement " << maxElement << std::endl;
        rIndex++;
    }

    std::cout << "Counting similartiy from distances... based on max=" << maxElement << std::endl;
    // rowId to columnId-similarity
    //std::vector<std::vector<int>> similarityV(rowCount, std::vector<int>(rowCount,0x0));

    for (int r = 0; r < rowCount; r++ )
    {
        for ( int c = 0; c < rowCount-r; c++ )
        {
            // Change from distance to similarity: 1 - x/max. same will have 1 value. distant will have 0
            distanceV[rowCount-r-1][rowCount-c-1] = (1 - distanceV[r][c]/maxElement); // TODO max element too big
        }
    }

    std::cout << "Stringify similarity and distance results..." << std::endl;
    // removeFile(summarySimilarityCoord) in caller
    std::ofstream out(similarityCoordsFile, std::ios::trunc | std::ios::out);
    if(!out.is_open())
        return;

    std::ostringstream oss;
    int lineCount = 0;
    int writeCount = 0;
    for (int r = 0; r < rowCount; r++ )
    {
        for ( int c = 0; c < rowCount-r; c++ )
        {
            oss << r << " " << c << " " << distanceV[r][c] << " " << distanceV[rowCount-r-1][rowCount-c-1] << std::endl;
            lineCount++;
        }
        const int k = 5000;
        if ( lineCount % rowCount/k )
        {
            writeCount++;
            std::cout << "\r" << "Saving results to file..." << writeCount << " out of " << (int)(rowCount*rowCount)/(int)(k/20) << std::flush;
            out << oss.str();
            out.seekp(0);
        }
    }
    std::cout << std::endl;

    out.flush();
    out.close();
}
