package it.unitn.nlpir.lab01;

import it.unitn.nlpir.readers.AnswerbagDocument;
import it.unitn.nlpir.readers.AnswerbagReader;

import java.io.File;
import java.io.IOException;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

public class QAIndex {
	public static final String EXAMPLE_TEST = "2503461	Where do I find the dtags to change information for mp3 players?";
	public static final String FIEILD_ID = "id";
	public static final String FIEILD_TEXT = "text";
	
	private static Document buildDocument(String qid, String text) {
		Document doc = new Document();
		doc.add(new Field(FIEILD_ID, qid, Field.Store.YES, Field.Index.NOT_ANALYZED));
		doc.add(new Field(FIEILD_TEXT, text, Field.Store.YES, Field.Index.ANALYZED));
		return doc;
	}

	public static void readAndIndexSingleFile(String fileName,
			IndexWriter writer) {
		AnswerbagReader reader = new AnswerbagReader(fileName);
		int count = 0;
		for (AnswerbagDocument doc : reader) {
			count++;
			try {
				writer.addDocument(buildDocument(doc.getId(), doc.getText()));
			} catch (IOException e) {
				e.printStackTrace();
			}
			if (count % 1000 == 0) {				
				System.out.printf("%d..", count);
			}
		}
		System.out.println("\nTotal documents read: " + count);
	}

	public static void main(String[] args) throws IOException, ParseException {
		// directory name to store the index
		File indexDir = new File(args[0]);
		// filename with the documents to index
		String fname = args[1];

		// create an index
		Directory index = FSDirectory.open(indexDir);

		StandardAnalyzer analyzer = new StandardAnalyzer(Version.LUCENE_35);
		IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_35,
				analyzer);

		// instantiate an IndexWriter
		IndexWriter writer = new IndexWriter(index, config);

		// read the file and write to the index
		readAndIndexSingleFile(fname, writer);
		writer.close();
	}
}