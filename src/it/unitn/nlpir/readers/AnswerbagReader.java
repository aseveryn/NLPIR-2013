package it.unitn.nlpir.readers;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Iterator;

public class AnswerbagReader implements Iterable<AnswerbagDocument> {

	String filename;
	
	public AnswerbagReader(String filename) {
		this.filename = filename;
	}
	
	class DocumentIterator implements Iterator<AnswerbagDocument> {
		private String line = null;
		private BufferedReader buf = null;
		
		public DocumentIterator(String filename) {
			try {
				buf = new BufferedReader(new FileReader(filename));
				this.line = buf.readLine();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		
		@Override
		public boolean hasNext() {
			try {
				this.line = buf.readLine();
			} catch (IOException e) {
				e.printStackTrace();
			}
			if (this.line == null) {
				try {
					buf.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
			return line != null;
		}

		@Override
		public AnswerbagDocument next() {
			String[] tokens = this.line.trim().split("\t");
			return new AnswerbagDocument(tokens[0], tokens[1]);
		}

		@Override
		public void remove() {
			throw new UnsupportedOperationException(); 
		}
		
		protected void finalize() throws Throwable {
			try {
				buf.close();
			} catch (IOException e) {
				e.printStackTrace();
			} finally {
				super.finalize();	
			}
		}
		
	}
	
	@Override
	public Iterator<AnswerbagDocument> iterator() {
		return new DocumentIterator(filename);
	}

}
