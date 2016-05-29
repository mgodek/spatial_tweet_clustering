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

    bool loadData(const char* stemmedFile, const char* stopWordFile);

    void countTfidf();

    void createStopWordList(double threshold, const char* stopWordFile);

    bool storeTfidfInFile(const char* tfidfFile, const char* dictFileName);

    // document index mapped to result for file
    typedef std::unordered_map<unsigned int, std::unordered_map<unsigned, double>*> TfIdfResults;
    inline TfIdfResults& getTfIdfResults() { return this->tfIdfResults; }

protected:

    double tfidf(size_t word, unsigned int docIndex);
    double tf(size_t word, unsigned int docIndex);
    double idf(size_t word);

    unsigned int _nextCoord;
    std::unordered_map<unsigned int, std::string> _dictionary;
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
                                       double      threshold,
                                       const char* stopWordFile )
    {
	parser->loadData(stemmedFile, stopWordFile);
	parser->countTfidf();

        parser->createStopWordList(threshold, stopWordFile);
    }

    void TFIDF_UseStopWordList_Run( StemmedFileInMemoryParser* parser,
                                    const char* stemmedFile,
                                    const char* tfidfFile,
                                    const char* stopWordFile,
                                    const char* dictFile )
    {
	parser->loadData(stemmedFile, stopWordFile);
	parser->countTfidf();

        parser->storeTfidfInFile(tfidfFile, dictFile);
    }
}

#endif // STEMMEDFILEINMEMORYPARSER_H
