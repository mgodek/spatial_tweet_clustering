#ifndef STEMMEDFILEINMEMORYPARSER_H
#define STEMMEDFILEINMEMORYPARSER_H

#include <string>
#include <functional>
#include <list>
#include <unordered_map>
#include <iostream>

class StemmedFileInMemoryParser
{
public:
  
  struct Feature {
    double countOfNonZero;
    double latitude;
    double longitude;
    double distanceFromZero;
    double distanceFromMax;
    double distanceFromMean;
    
    Feature():
    countOfNonZero(0.0),
    latitude(0.0),
    longitude(0.0),
    distanceFromMax(0.0),
    distanceFromMean(0.0)
    {};
  };
  
  StemmedFileInMemoryParser();

  virtual ~StemmedFileInMemoryParser();

  bool loadData(const char* stemmedFile, const char* stopWordFile);

  void countTfidf();

  void createStopWordList(double thresholdUpper, double thresholdBottom, unsigned int stopWordCountBottom, const char* stopWordFile);

  bool storeTfidfInFile(const char* tfidfFile, const char* dictFileName);
  
  void countFeatures();
  
  void storeFeatures(const char* featureFile);

  // document index mapped to result for file
  typedef std::unordered_map<unsigned int, std::unordered_map<unsigned, double>*> TfIdfResults;
  inline TfIdfResults& getTfIdfResults() { return this->tfIdfResults; }

protected:
  
  void normalizeFeatures();
  double tfidf(size_t word, unsigned int docIndex);
  double tf(size_t word, unsigned int docIndex);
  double idf(size_t word);

  unsigned int _nextCoord;
  Feature _max;
  Feature _min;
  std::unordered_map<unsigned int, std::pair<double, double>> _geoPerDoc;
  std::unordered_map<unsigned int, std::pair<std::string, unsigned int>> _dictionary;
  std::unordered_map<unsigned int, Feature> _dataFeatures;
  double minimalValue;
  double quant;
  std::unordered_map<size_t, unsigned int> _wordsToCoords;
  std::unordered_map<size_t, unsigned int> _globalWordsCount;
  std::list<std::pair<unsigned int, std::string>> _docName;
  std::unordered_map<unsigned int, unsigned int> _docsLens;
  std::unordered_map<size_t, unsigned int> _numberOfDocumentsWithGivenWords;
  std::unordered_map<unsigned int, std::unordered_map<size_t, unsigned int>* > _wordsCountPerDocument;
  TfIdfResults tfIdfResults;

  std::hash<std::string> hash_fn;

  static double MinimalValueLowerBound;

};

extern "C" {
  StemmedFileInMemoryParser* TFIDF_New()
  {
      return new StemmedFileInMemoryParser();
  }

  void TFIDF_CreateStopWordList_Run( StemmedFileInMemoryParser* parser,
				      const char* stemmedFile,
				      const char* tfidfFile,
				      double      thresholdUpper,
				      double      thresholdBottom,
				      unsigned int stopWordCountBottom,
				      const char* stopWordFile )
  {
      parser->loadData(stemmedFile, stopWordFile);
      parser->countTfidf();

      parser->createStopWordList(thresholdUpper, thresholdBottom, stopWordCountBottom, stopWordFile);
  }

  void TFIDF_UseStopWordList_Run( StemmedFileInMemoryParser* parser,
				  const char* stemmedFile,
				  const char* tfidfFile,
				  const char* stopWordFile,
				  const char* dictFile,
				  const char* featureFile )
  {
      parser->loadData(stemmedFile, stopWordFile);
      parser->countTfidf();
      parser->countFeatures();
      parser->storeTfidfInFile(tfidfFile, dictFile);
      parser->storeFeatures(featureFile);
      std::cout << "Done with all in TFIDF_UseStopWordList_Run" << std::endl;
  }

  void CountCoordinateSimilarity( const char* parsedCoordsFile,
				  const char* similarityCoordsFile );
}

#endif // STEMMEDFILEINMEMORYPARSER_H
