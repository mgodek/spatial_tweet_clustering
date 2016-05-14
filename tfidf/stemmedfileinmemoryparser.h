#ifndef STEMMEDFILEINMEMORYPARSER_H
#define STEMMEDFILEINMEMORYPARSER_H

#include <string>
#include <functional>
#include <list>
#include <unordered_map>

class StemmedFileInMemoryParser
{
public:
    StemmedFileInMemoryParser();

    virtual ~StemmedFileInMemoryParser();

    bool loadData(const char* fileName);

    void countTfidf();

    bool storeTfidfInFile(const char* fileName);

    inline std::list<std::unordered_map<unsigned, double>*>& getTfIdfResults() { return this->tfIdfResults; }

protected:

    double tfidf(size_t word, unsigned int docIndex);
    double tf(size_t word, unsigned int docIndex);
    double idf(size_t word);

    unsigned int _nextCoord;
    double minimalValue;
    double quant;
    std::unordered_map<size_t, unsigned int> _wordsToCoords;
    std::unordered_map<unsigned int, size_t> _coordsToWords;
    std::unordered_map<size_t, unsigned int> _globalWordsCount;
    std::unordered_map<unsigned int, unsigned int> _docsLens;
    std::unordered_map<size_t, unsigned int> _numberOfDocumentsWithGivenWords;
    std::unordered_map<unsigned int, std::unordered_map<size_t, unsigned int>* > _wordsCountPerDocument;
    std::list<std::unordered_map<unsigned, double>*> tfIdfResults;

    std::hash<std::string> hash_fn;

    static double MinimalValueLowerBound;

};

#endif // STEMMEDFILEINMEMORYPARSER_H
