package it.unitn.nlpir.lab01;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

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

public class QAInteractive {
	
	public static void main(String[] args) throws CorruptIndexException,
			IOException {

		// path to the directory containing Lucene index
		File indexDir = new File(args[0]);
		
		// maximum number of documents to retrieve for each query
		int maxHits = Integer.parseInt(args[1]);

		System.out.println("Index Dir = " + indexDir.getCanonicalPath());

		// open the index
		Directory dir = FSDirectory.open(indexDir);
		IndexReader reader = IndexReader.open(dir);

		// instantiate a searcher
		IndexSearcher searcher = new IndexSearcher(reader);
		
		Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_35);
		QueryParser parser = new QueryParser(Version.LUCENE_35, QAIndex.FIEILD_TEXT, analyzer);
	    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
	    while (true) {
	    	System.out.print("Your question: ");
	    	String query = br.readLine();
	    	if (query.trim().isEmpty())
	    		break;
	    	String qtext = query.replaceAll("[^A-Za-z0-9]", " ");
			// System.err.printf("%s %s\n", qid, qtext);
			Query q;
			try {
				q = parser.parse(qtext);
			} catch (ParseException e) {
				System.err.println("Failed to parse the query! Skipping...");
				continue;
			}

			// search for a query retrieving maxHits results
			TopDocs hits = searcher.search(q, maxHits);

			// write the results to standard output in the following format:
			// <question id> <answer id> <score of the SE>
			System.out.printf("%d documents retrieved\n", hits.scoreDocs.length);
			for (ScoreDoc sd : hits.scoreDocs) {
				float score = sd.score;
				int docId = sd.doc;
				Document document = searcher.doc(docId);					
				String aid = document.get(QAIndex.FIEILD_ID);
				String text = document.get(QAIndex.FIEILD_TEXT);
				System.out.printf("%s\t%.8f\t%s\n", aid, score, text);
			}
	    }
	    System.out.printf("exiting...");
	    searcher.close();
	}
}
