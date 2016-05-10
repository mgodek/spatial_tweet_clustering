#ifndef TFIDFHISTOGRAMGENERATOR_H
#define TFIDFHISTOGRAMGENERATOR_H

#include "exceptions/ioexception.h"

#include <list>
#include <unordered_map>

class TfidfHistogramGenerator
{
public:
    TfidfHistogramGenerator();
    ~TfidfHistogramGenerator();

    void generateHistograms(const std::list<std::unordered_map<unsigned, double> *> &tfIdfData);
    void generateHistograms(const char* tfidfFileName) throw(IOException);

    void save(const char* histogramsFileName) throw(IOException);

    void loadCoordsHistogram(const char* file) throw(IOException);
    void loadDimsHistogram(const char* file) throw(IOException);

    const std::unordered_map<double, unsigned> &getCoordsValuesFrequency() const;

    const std::unordered_map<unsigned, unsigned> &getNonZeroCoordsFrequency() const;

private:

    void saveCoords(const char* fileName) throw(IOException);
    void saveDims(const char* fileName) throw(IOException);
    std::ifstream *openFileToRead(const char *file) throw(IOException);
    std::ofstream *openFileToWrite(const char *file) throw(IOException);

    double quant;

    std::unordered_map<double, unsigned> coordsValuesFrequency;
    std::unordered_map<unsigned, unsigned> nonZeroCoordsFrequency;
};

#endif // TFIDFHISTOGRAMGENERATOR_H
