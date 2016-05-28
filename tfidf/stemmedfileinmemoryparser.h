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

    // document index mapped to result for file
    typedef std::unordered_map<unsigned int, std::unordered_map<unsigned, double>*> TfIdfResults;
    inline TfIdfResults& getTfIdfResults() { return this->tfIdfResults; }

protected:

    double tfidf(size_t word, unsigned int docIndex);
    double tf(size_t word, unsigned int docIndex);
    double idf(size_t word);

    unsigned int _nextCoord;
    std::list<std::pair<unsigned int, std::string>> _dictionary;
    double minimalValue;
    double quant;
    std::unordered_map<size_t, unsigned int> _wordsToCoords;
    std::unordered_map<unsigned int, size_t> _coordsToWords;
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

    void TFIDF_Run( StemmedFileInMemoryParser* parser, const char* fileNameIn, const char* fileNameOut )
    {
	parser->loadData(fileNameIn);
	parser->countTfidf();
	parser->storeTfidfInFile(fileNameOut);
    }
}

#endif // STEMMEDFILEINMEMORYPARSER_H
