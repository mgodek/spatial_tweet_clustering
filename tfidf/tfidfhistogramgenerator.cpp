#include "tfidfhistogramgenerator.h"
#include "exceptions/ioexception.h"
#include "readers/normalizedformatdatareader.h"

#include <cfloat>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

TfidfHistogramGenerator::TfidfHistogramGenerator():
    quant(DBL_MAX)
{

}

TfidfHistogramGenerator::~TfidfHistogramGenerator()
{

}

void TfidfHistogramGenerator::generateHistograms(const std::list<std::unordered_map<unsigned, double>*> &tfIdfData)
{
    for(const std::unordered_map<unsigned, double>* vec: tfIdfData)
    {
        if(this->nonZeroCoordsFrequency.count(vec->size() == 0))
            this->nonZeroCoordsFrequency.insert({vec->size(), 1});
        else
            this->nonZeroCoordsFrequency[vec->size()] += 1;
        for(const std::pair<unsigned, double>& pair : *vec)
        {
            if(this->quant > pair.second) // should be bigger then DBL_MIN times 5
                this->quant = pair.second;
            if(this->coordsValuesFrequency.count(pair.second) == 0)
                this->coordsValuesFrequency.insert({pair.second, 1});
            else
                this->coordsValuesFrequency[pair.second] += 1;
        }
    }
}

void TfidfHistogramGenerator::generateHistograms(const char *tfidfFileName) throw(IOException)
{
    std::ifstream in(tfidfFileName, std::ios::in);
    if(!in.is_open())
        throw IOException(Utils::getInstance()->concatenate(tfidfFileName, " can't be open to read."));
    NormalizedFormatDataReader reader;
    AbstractPointsSpace<SparsePoint> * space = reader.parseFile(&in);
    for(unsigned i = 0; i < space->getNumPoints(); ++i) {
        PtrCAbstractPoint p = space->getPoint(i);
        if(this->nonZeroCoordsFrequency.count(p->size()) == 0)
            this->nonZeroCoordsFrequency.insert({p->size(), 1});
        else
            this->nonZeroCoordsFrequency[p->size()] += 1;
        for(unsigned key: p->getKeys()) {
            if(this->coordsValuesFrequency.count((*p)[key]) == 0)
                this->coordsValuesFrequency.insert({(*p)[key], 1});
            else
                this->coordsValuesFrequency[(*p)[key]] += 1;
        }
    }

    this->quant = space->getQuant();
    delete space;
}

void TfidfHistogramGenerator::save(const char *histogramsFileName) throw(IOException)
{
    this->saveCoords(Utils::getInstance()->concatenate(histogramsFileName, ".chist"));
    this->saveDims(Utils::getInstance()->concatenate(histogramsFileName, ".dhist"));
}



void TfidfHistogramGenerator::loadCoordsHistogram(const char *file) throw(IOException)
{
    std::ifstream* in = openFileToRead(file);
    while(!in->eof()) {
        double one;
        unsigned two;
        *in >> one >> two;
        this->coordsValuesFrequency.insert({one, two});
    }
    in->close();
    delete in;
}

void TfidfHistogramGenerator::loadDimsHistogram(const char *file) throw(IOException)
{
    std::ifstream* in = openFileToRead(file);
    while(!in->eof()) {
        unsigned one, two;
        *in >> one >> two;
        this->nonZeroCoordsFrequency.insert({one, two});
    }
    in->close();
    delete in;
}

void TfidfHistogramGenerator::saveCoords(const char *fileName) throw(IOException)
{
    std::ofstream* out = openFileToWrite(fileName);
    for(std::pair<double, unsigned> pair: this->coordsValuesFrequency) {
        *out << pair.first << " " << pair.second << std::endl;
    }
    out->flush();
    out->close();
    delete out;
}

void TfidfHistogramGenerator::saveDims(const char *fileName) throw(IOException)
{
    std::ofstream* out = openFileToWrite(fileName);
    for(std::pair<unsigned, unsigned> pair: this->nonZeroCoordsFrequency) {
        *out << pair.first << " " << pair.second << std::endl;
    }
    out->flush();
    out->close();
    delete out;
}

std::ifstream* TfidfHistogramGenerator::openFileToRead(const char *file) throw(IOException)
{
    std::ifstream* in = new std::ifstream(file, std::ios::in);
    if(!in->is_open())
        throw IOException(Utils::getInstance()->concatenate(file, " can't be open to read."));
    return in;
}

std::ofstream *TfidfHistogramGenerator::openFileToWrite(const char *file) throw(IOException)
{
    std::ofstream* out = new std::ofstream(file, std::ios::out | std::ios::trunc);
    if(!out->is_open())
        throw IOException(Utils::getInstance()->concatenate(file, " can't be open to write."));
    return out;
}
const std::unordered_map<unsigned, unsigned>& TfidfHistogramGenerator::getNonZeroCoordsFrequency() const
{
    return this->nonZeroCoordsFrequency;
}

const std::unordered_map<double, unsigned>& TfidfHistogramGenerator::getCoordsValuesFrequency() const
{
    return this->coordsValuesFrequency;
}
