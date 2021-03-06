/* This is a simple program which uses libstemmer to provide a command
 * line interface for stemming using any of the algorithms provided.
 */

#include "stemwords.h"

int
main(int argc, char * argv[])
{
    char * in = 0;
    char * out = 0;
    FILE * f_in;
    FILE * f_out;
    struct sb_stemmer * stemmer;

    char * language = "english";
    char * charenc = NULL;

    char * s;
    int i = 1;
    pretty = 0;

    progname = argv[0];

    while(i < argc) {
	s = argv[i++];
	if (s[0] == '-') {
	    if (strcmp(s, "-o") == 0) {
		if (i >= argc) {
		    fprintf(stderr, "%s requires an argument\n", s);
		    exit(1);
		}
		out = argv[i++];
	    } else if (strcmp(s, "-i") == 0) {
		if (i >= argc) {
		    fprintf(stderr, "%s requires an argument\n", s);
		    exit(1);
		}
		in = argv[i++];
	    } else if (strcmp(s, "-l") == 0) {
		if (i >= argc) {
		    fprintf(stderr, "%s requires an argument\n", s);
		    exit(1);
		}
		language = argv[i++];
	    } else if (strcmp(s, "-c") == 0) {
		if (i >= argc) {
		    fprintf(stderr, "%s requires an argument\n", s);
		    exit(1);
		}
		charenc = argv[i++];
	    } else if (strcmp(s, "-p2") == 0) {
		pretty = 2;
	    } else if (strcmp(s, "-p") == 0) {
		pretty = 1;
	    } else if (strcmp(s, "-h") == 0) {
		usage(0);
	    } else {
		fprintf(stderr, "option %s unknown\n", s);
		usage(1);
	    }
	} else {
	    fprintf(stderr, "unexpected parameter %s\n", s);
	    usage(1);
	}
    }

    /* prepare the files */
    f_in = (in == 0) ? stdin : fopen(in, "r");
    if (f_in == 0) {
	fprintf(stderr, "file %s not found\n", in);
	exit(1);
    }
    f_out = (out == 0) ? stdout : fopen(out, "w");
    if (f_out == 0) {
	fprintf(stderr, "file %s cannot be opened\n", out);
	exit(1);
    }

    /* do the stemming process: */
    stemmer = sb_stemmer_new(language, charenc);
    if (stemmer == 0) {
        if (charenc == NULL) {
            fprintf(stderr, "language `%s' not available for stemming\n", language);
            exit(1);
        } else {
            fprintf(stderr, "language `%s' not available for stemming in encoding `%s'\n", language, charenc);
            exit(1);
        }
    }
    stem_file(stemmer, f_in, f_out);
    sb_stemmer_delete(stemmer);

    if (in != 0) (void) fclose(f_in);
    if (out != 0) (void) fclose(f_out);

    return 0;
}

