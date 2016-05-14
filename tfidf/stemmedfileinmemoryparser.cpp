#include "stemmedfileinmemoryparser.h"

#include <cmath>
#include <cfloat>
#include <fstream>
#include <functional>
#include <iostream>
#include <string>
#include <sstream>

//#include <QMap>
/// We don't care for DBL_MIN, so quantization has to be at 2*DBL_MIN,
/// so smallest values have to be 4*DBL_MIN, so minimal value has to be bigger
/// then that.
double StemmedFileInMemoryParser::MinimalValueLowerBound = DBL_MIN * 5;

StemmedFileInMemoryParser::StemmedFileInMemoryParser():
    _nextCoord(0),
    minimalValue(DBL_MAX)
{
}

StemmedFileInMemoryParser::~StemmedFileInMemoryParser()
{
    for(auto pair : this->_wordsCountPerDocument)
    {
        delete pair.second;
        pair.second = 0;
    }

    for(auto map : this->tfIdfResults)
    {
        delete map;
        map = 0;
    }
}

bool StemmedFileInMemoryParser::loadData(const char *fileName)
{
    std::ifstream in(fileName, std::ios::in);
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
        while(!inner.eof())
        {
            std::string word;
            inner >> word;
            ++lineLen;
            size_t hash = this->hash_fn(word);
            if(this->_wordsToCoords.count(hash) == 0)
                this->_wordsToCoords.insert({hash, _nextCoord++});
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
        unsigned docIndex = docNumber++;
        this->_docsLens.insert({docIndex, lineLen});
        this->_wordsCountPerDocument.insert({docIndex, doc});
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
        this->tfIdfResults.push_back(map);
    }
    this->quant = this->minimalValue / 4;
}

bool StemmedFileInMemoryParser::storeTfidfInFile(const char *fileName)
{
    std::ofstream out(fileName, std::ios::trunc | std::ios::out);
    if(!out.is_open())
        return false;
    out << _wordsCountPerDocument.size() << " "
        << _nextCoord << " " << this->quant << std::endl; // header format: <number of vectors> <number of dimensions> <quantization value>
    for(auto map : this->tfIdfResults)
    { // for all docs
        for(auto pair : *map)
        { // for all words in doc - counting tfidf
            if(pair.second < DBL_MIN)
                pair.second = this->minimalValue / 2;
            out << pair.first << ':' << pair.second << ' ';
        }
        out << std::endl;
    }
    out << std::ends;
    out.flush();
    out.close();
}
