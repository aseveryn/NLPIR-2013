package it.unitn.nlpir.lab01;

import java.io.IOException;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.RAMDirectory;
import org.apache.lucene.util.Version;

public class HelloLucene {
	private static final String TEXT_FIELD = "text";

	private static void addDoc(IndexWriter w, String value) throws IOException {
		Document doc = new Document();
		doc.add(new Field(TEXT_FIELD, value, Field.Store.YES,
				Field.Index.ANALYZED));
		w.addDocument(doc);
	}

	public static void main(String[] args) throws IOException, ParseException {
		// 0. Specify the analyzer for tokenizing text.
		// The same analyzer should be used for indexing and searching
//		StandardAnalyzer analyzer = new StandardAnalyzer(Version.LUCENE_35);
		StemAnalyzer analyzer = new StemAnalyzer(Version.LUCENE_35);

		// 1. create the index
		Directory index = new RAMDirectory();

		IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_35,
				analyzer);

		IndexWriter w = new IndexWriter(index, config);
		addDoc(w, "Learn Lucene with Ease");
		addDoc(w, "Learning Lucene");
		addDoc(w, "Lucene in Action");
		addDoc(w, "Lucene for Dummies");
		addDoc(w, "Managing Gigabytes");
		addDoc(w, "The Art of Computer Science");
		w.close();

		// 2. query
		String querystr = "lucene is easy to learn";

		// the "title" arg specifies the default field to use
		// when no field is explicitly specified in the query.
		querystr = "(lucene) AND (dummy)";
		Query q = new QueryParser(Version.LUCENE_35, TEXT_FIELD, analyzer)
				.parse(querystr);
		System.out.println("Query: " + q.toString());
		
		// Using boolean queries.
//		Query query1 = new TermQuery(new Term(TEXT_FIELD, "lucene"));
//		Query query2 = new TermQuery(new Term(TEXT_FIELD, "dummies"));
//
//		BooleanQuery booleanQuery = new BooleanQuery();
//		booleanQuery.add(query1, BooleanClause.Occur.MUST);
//		booleanQuery.add(query2, BooleanClause.Occur.MUST_NOT);
//		System.out.println("Query: " + booleanQuery.toString());

		// 3. search
		int hitsPerPage = 10;
		IndexSearcher searcher = new IndexSearcher(IndexReader.open(index));
		TopScoreDocCollector collector = TopScoreDocCollector.create(
				hitsPerPage, true);
		searcher.search(q, collector);
		ScoreDoc[] hits = collector.topDocs().scoreDocs;

		// 4. display results
		System.out.println("Found " + hits.length + " hits.");
		for (ScoreDoc sd : hits) {
			int docId = sd.doc;
			Document d = searcher.doc(docId);
			System.out.println(sd.score + ". " + d.get(TEXT_FIELD));
		}

		// searcher can only be closed when there
		// is no need to access the documents any more.
		searcher.close();
	}
}
