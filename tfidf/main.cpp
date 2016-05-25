#include "stemmedfileinmemoryparser.h"

int main(int argc, char** argv)
{
  StemmedFileInMemoryParser parser;
  parser.loadData("tweetsStemmed.txt", true);
  // Assuming file format as: tweet_id stem stem stem stem ..... (white space separated)
  parser.countTfidf();
  parser.storeTfidfInFile("tweetsTfIdf.txt");
  return 0;
}
