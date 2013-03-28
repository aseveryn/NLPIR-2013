package it.unitn.nlpir.lab02;

import it.unitn.nlpir.lab01.QAIndex;
import it.unitn.nlpir.readers.AnswerbagDocument;
import it.unitn.nlpir.readers.AnswerbagReader;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.CorruptIndexException;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

public class QARetrieval {

	public static void readQueriesAndSearch(String fileName,
			IndexSearcher searcher, int maxHits) throws CorruptIndexException,
			IOException, ParseException {

		String defaultField = "text";
		// we use the same StandardAnalyzer we used for indexing
		Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_35);
//		Analyzer analyzer = new StemAnalyzer(Version.LUCENE_35);		
		QueryParser parser = new QueryParser(Version.LUCENE_35, defaultField,
				analyzer);
		AnswerbagReader reader = new AnswerbagReader(fileName);
		String outFileName = fileName + ".results";
		try (BufferedWriter buf = new BufferedWriter(
				new FileWriter(outFileName))) {
			for (AnswerbagDocument question : reader) {
				String qid = question.getId();
				String qtext = question.getText().replaceAll("[^A-Za-z0-9]",
						" ");
				Query q = parser.parse(qtext);
				
				// search for a query retrieving maxHits results
				TopDocs hits = searcher.search(q, maxHits);
				System.out.printf("Query: %s (%d documents retrieved)\n", qid, hits.scoreDocs.length);
				// write the results to standard output in the following format:
				for (ScoreDoc sd : hits.scoreDocs) {
					float score = sd.score;
					int docId = sd.doc;
					Document document = searcher.doc(docId);
					String aid = document.get(QAIndex.FIEILD_ID);
					String relevant = qid.equals(aid) ? "true" : "false";
					String resLine = String.format("%s\t%s\t%.8f\t%s\n", qid, aid, score,
							relevant);
					buf.write(resLine);
				}
			}
		}
		System.out.printf("Results written to: %s\n", outFileName);
	}

	public static void main(String[] args) throws CorruptIndexException,
			IOException {

		if (args.length != 3) {
			System.err.println("Wrong number of arguments!");
			System.err
					.println("Usage: java QARetrieval <index_dir> <queries> <maxHits>");
			System.exit(1);
		}
		// path to the directory containing Lucene index
		File indexDir = new File(args[0]);

		// file containing the queries
		String queryFileName = args[1];

		// maximum number of documents to retrieve for each query
		int maxHits = Integer.parseInt(args[2]);

		System.out.println("Index Dir = " + indexDir.getCanonicalPath());

		// open the index
		Directory dir = FSDirectory.open(indexDir);
		IndexReader reader = IndexReader.open(dir);

		// instantiate a searcher
		IndexSearcher searcher = new IndexSearcher(reader);

		// process queries and search
		try {
			readQueriesAndSearch(queryFileName, searcher, maxHits);
		} catch (ParseException e) {
			e.printStackTrace();
		}
	}

}