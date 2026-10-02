import React, { useState, useEffect } from 'react';
import { BookOpen, Search, FileText, CheckCircle, ExternalLink, Loader2, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { KnowledgeDoc, SearchResult } from '../types';

export const KnowledgeBasePage: React.FC = () => {
  const [docs, setDocs] = useState<KnowledgeDoc[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    try {
      const data = await api.getDocuments();
      setDocs(data);
    } catch (e) {
      console.error('Failed to load documents:', e);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const data = await api.searchDocuments(searchQuery);
      setSearchResults(data.results || []);
    } catch (e) {
      console.error('Search failed:', e);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
      {/* Header */}
      <div>
        <h1 className="text-lg font-semibold text-slate-900 tracking-tight flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-emerald-600" />
          <span>Technical Knowledge Base & RAG Index</span>
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Operational runbooks, incident post-mortems, and architecture documents vectorized in PostgreSQL + pgvector.
        </p>
      </div>

      {/* Semantic Vector Search Input */}
      <form onSubmit={handleSearch} className="relative">
        <div className="relative rounded-xl border border-slate-200 bg-white shadow-subtle focus-within:border-emerald-500 focus-within:ring-2 focus-within:ring-emerald-100 transition-all flex items-center p-2">
          <Search className="w-4 h-4 text-slate-400 ml-2 mr-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search runbooks via vector similarity (e.g., 'how to troubleshoot connection pool timeouts')..."
            className="flex-1 text-xs text-slate-900 placeholder:text-slate-400 outline-none bg-transparent"
          />
          <button
            type="submit"
            disabled={!searchQuery.trim() || isSearching}
            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-100 disabled:text-slate-400 text-white text-xs font-medium transition-colors shadow-sm"
          >
            {isSearching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Vector Search'}
          </button>
        </div>
      </form>

      {/* Search Results Display */}
      {searchResults.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
            <span>Semantic Vector Matches ({searchResults.length})</span>
            <button
              onClick={() => setSearchResults([])}
              className="text-[11px] text-slate-400 hover:text-slate-600 lowercase"
            >
              clear search
            </button>
          </h2>

          <div className="grid grid-cols-1 gap-3">
            {searchResults.map((res, i) => (
              <div key={i} className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/20 shadow-subtle space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-emerald-700" />
                    <span className="text-xs font-semibold text-slate-900">{res.document_title}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
                      {res.heading}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                    Similarity Score: {res.score}
                  </span>
                </div>
                <pre className="text-xs text-slate-700 font-sans whitespace-pre-wrap leading-relaxed bg-white p-3 rounded-lg border border-slate-200">
                  {res.content}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Ingested Documents Grid */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Ingested Runbooks & Post-Mortems
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {docs.map((doc, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 shadow-subtle space-y-3 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-lg bg-slate-100 text-slate-700 border border-slate-200">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-slate-900">{doc.title}</h3>
                    <p className="text-[10px] text-slate-500 font-mono">{doc.source}</p>
                  </div>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                  {doc.chunks_count || 3} chunks
                </span>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                <span className="flex items-center space-x-1 text-emerald-700 font-medium">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Vectorized & Indexed</span>
                </span>
                <button
                  onClick={() => {
                    setSearchQuery(doc.title);
                    api.searchDocuments(doc.title).then((d) => setSearchResults(d.results || []));
                  }}
                  className="text-slate-600 hover:text-emerald-700 font-medium flex items-center space-x-1"
                >
                  <span>Query Chunks</span>
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
