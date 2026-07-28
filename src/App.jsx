import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ArrowDownToLine,
  ArrowUpRight,
  BookOpen,
  BrainCircuit,
  Check,
  Code2,
  Copy,
  FileText,
  GraduationCap,
  ImagePlus,
  Languages,
  LayoutDashboard,
  Lightbulb,
  LoaderCircle,
  Menu,
  MessageSquareText,
  Moon,
  Play,
  Plus,
  RotateCcw,
  Sparkles,
  Sun,
  Upload,
  X,
  Zap,
} from 'lucide-react';

const navItems = [
  { label: 'Overview', bn: 'ওভারভিউ', icon: LayoutDashboard },
  { label: 'My Boards', bn: 'আমার বোর্ড', icon: BookOpen },
  { label: 'Flashcards', bn: 'ফ্ল্যাশকার্ড', icon: BrainCircuit },
];

function toWorkspaceResult(payload) {
  const notes = payload.clean_notes_markdown || '';
  const lines = notes.split('\n').map((line) => line.trim());
  const headings = [];
  const bulletPoints = [];

  lines.forEach((line, index) => {
    const heading = line.match(/^#{1,6}\s+(.+)/);
    const bullet = line.match(/^[-*+]\s+(.+)/);
    if (heading) {
      const description = lines.slice(index + 1).find((next) => next && !next.startsWith('#') && !/^[-*+]\s+/.test(next)) || '';
      headings.push({ title: heading[1].replace(/[*_`]/g, ''), description: description.replace(/[*_`]/g, '') });
    }
    if (bullet) bulletPoints.push(bullet[1].replace(/[*_`]/g, ''));
  });

  return {
    title: payload.title || 'Extracted study guide',
    languages: payload.detected_languages?.length ? payload.detected_languages : ['Unknown'],
    confidence: Math.round((Number(payload.confidence) || 0) * 100),
    summary: payload.bangla_explanation || 'পড়ার মতো স্পষ্ট লেখা পাওয়া যায়নি।',
    notes,
    headings: headings.length ? headings : [{ title: payload.title || 'Clean notes', description: notes || 'No readable text was extracted.' }],
    bullets: bulletPoints.length ? bulletPoints : ['সম্পূর্ণ নোট দেখতে Study guide অংশটি দেখুন।'],
    code: Array.isArray(payload.code_snippets) ? payload.code_snippets : [],
    flashcards: Array.isArray(payload.flashcards) ? payload.flashcards : [],
    unclear: Array.isArray(payload.unclear_sections) && payload.unclear_sections.length
      ? payload.unclear_sections
      : ['কোনো অস্পষ্ট অংশ চিহ্নিত হয়নি।'],
  };
}

function App() {
  const [activeTab, setActiveTab] = useState('guide');
  const [activeNav, setActiveNav] = useState('Overview');
  const [imageUrl, setImageUrl] = useState(null);
  const [fileName, setFileName] = useState('');
  const [result, setResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const [toast, setToast] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!toast) return undefined;
    const timer = window.setTimeout(() => setToast(''), 3200);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const processFile = useCallback(async (file) => {
    if (!file || !file.type.startsWith('image/')) {
      setToast('শুধু JPG, PNG বা WEBP image upload করুন।');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setToast('Image file অবশ্যই 10 MB-এর ছোট হতে হবে।');
      return;
    }

    setFileName(file.name);
    setImageUrl(URL.createObjectURL(file));
    setResult(null);
    setIsProcessing(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const body = new FormData();
      body.append('file', file);
      const response = await fetch(`${apiUrl.replace(/\/$/, '')}/api/extract`, { method: 'POST', body });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Image analysis failed.');
      setResult(toWorkspaceResult(payload));
      setToast('আপনার study guide তৈরি হয়েছে।');
    } catch (error) {
      setToast(error.message || 'AI service পাওয়া যায়নি। আবার চেষ্টা করুন।');
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const resetWorkspace = () => {
    setImageUrl(null);
    setFileName('');
    setResult(null);
    setActiveTab('guide');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const downloadMarkdown = () => {
    if (!result) return;
    const markdown = `# ${result.title}\n\n## সহজ বাংলায়\n${result.summary}\n\n${result.notes}\n\n## Flashcards\n${result.flashcards.map((card) => `- **Q:** ${card.question}\n  **A:** ${card.answer}`).join('\n')}`;
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${result.title.replaceAll(' ', '-').toLowerCase() || 'board2learn-study-guide'}.md`;
    anchor.click();
    URL.revokeObjectURL(url);
    setToast('Markdown download শুরু হয়েছে।');
  };

  return (
    <div className={darkMode ? 'app dark' : 'app'}>
      <aside className={mobileNav ? 'sidebar mobile-open' : 'sidebar'}>
        <div className="brand">
          <div className="brand-mark"><Sparkles size={18} /></div>
          <div><strong>Board2Learn</strong><span>BD</span></div>
          <button className="icon-button sidebar-close" onClick={() => setMobileNav(false)} aria-label="Close menu"><X size={17} /></button>
        </div>
        <div className="workspace-switcher">
          <div className="workspace-avatar">B</div>
          <div><small>WORKSPACE</small><b>Study workspace</b></div>
        </div>
        <nav className="main-nav">
          <small className="nav-label">WORKSPACE</small>
          {navItems.map(({ label, bn, icon: Icon }) => (
            <button className={activeNav === label ? 'nav-item active' : 'nav-item'} key={label} onClick={() => { setActiveNav(label); setMobileNav(false); }}>
              <Icon size={18} /><span>{label}<em>{bn}</em></span>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="progress-card"><div className="progress-orb"><GraduationCap size={19} /></div><div><b>আজকের progress</b><span>বোর্ড upload করে পড়া শুরু করুন</span></div><ArrowUpRight size={16} /></div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button className="icon-button menu-button" onClick={() => setMobileNav(true)} aria-label="Open menu"><Menu size={20} /></button>
          <div className="breadcrumbs"><span>Workspace</span><b>/</b><strong>New board</strong></div>
          <div className="top-actions"><button className="icon-button" onClick={() => setDarkMode((value) => !value)} aria-label="Toggle theme">{darkMode ? <Sun size={18} /> : <Moon size={18} />}</button><div className="language"><Languages size={16} /><span>বাংলা</span></div></div>
        </header>

        <div className="page-wrap">
          <section className="hero">
            <div><div className="eyebrow"><span className="live-dot" /> AI STUDY WORKSPACE</div><h1>Board থেকে <span>বোঝাপড়া</span> তৈরি হোক।</h1><p>আপনার whiteboard বা class note upload করুন। AI সেটাকে সহজ বাংলায় একটি interactive study guide-এ বদলে দেবে।</p></div>
            <div className="hero-decoration"><div className="scribble">learn<br /><span>smarter</span></div><div className="spark spark-one">✦</div><div className="spark spark-two">✧</div></div>
          </section>

          <section className="upload-card">
            <div className="section-heading"><div><h2>একটি board upload করুন</h2><p>হাতের লেখা, diagram, code বা formula—সব একসাথে বুঝতে পারবে।</p></div><div className="supported"><ImagePlus size={15} /> JPG, PNG, WEBP · max 10MB</div></div>
            {!imageUrl ? (
              <div className={isDragging ? 'dropzone dragging' : 'dropzone'} onDragOver={(event) => { event.preventDefault(); setIsDragging(true); }} onDragLeave={() => setIsDragging(false)} onDrop={(event) => { event.preventDefault(); setIsDragging(false); processFile(event.dataTransfer.files?.[0]); }} onClick={() => fileInputRef.current?.click()}>
                <input ref={fileInputRef} type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => processFile(event.target.files?.[0])} hidden />
                <div className="upload-icon"><Upload size={22} /></div><h3>ছবিটি এখানে drop করুন</h3><p>অথবা আপনার device থেকে select করুন</p><button className="primary-button" onClick={(event) => { event.stopPropagation(); fileInputRef.current?.click(); }}><Plus size={17} /> Choose image</button><small>আপনার ছবি শুধু analysis-এর জন্য ব্যবহার করা হয়</small>
              </div>
            ) : (
              <div className="uploaded-state"><div className="preview-wrap"><img src={imageUrl} alt="Uploaded whiteboard" /><div className="image-overlay"><Check size={16} /> Uploaded</div></div><div className="file-details"><div className="file-title"><FileText size={19} /><div><b>{fileName}</b><span>{isProcessing ? 'Analysis চলছে...' : 'Analysis complete'}</span></div></div>{isProcessing ? <div className="processing"><LoaderCircle size={17} className="spin" /><div><b>Board পড়া হচ্ছে...</b><span>Gemini আপনার notes এবং structure বুঝছে</span></div></div> : <div className="ready-state"><Check size={16} /><span>Study guide প্রস্তুত</span></div>}<div className="file-actions"><button className="secondary-button" onClick={() => fileInputRef.current?.click()}><Upload size={15} /> Replace</button><button className="text-button" onClick={resetWorkspace}><RotateCcw size={15} /> Clear</button><input ref={fileInputRef} type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => processFile(event.target.files?.[0])} hidden /></div></div></div>
            )}
          </section>

          {result && <section className="result-section">
            <div className="result-header"><div><div className="eyebrow"><span className="check-dot"><Check size={12} /></span> ANALYSIS COMPLETE</div><h2>আপনার study guide ready</h2><p>Board-এর গুরুত্বপূর্ণ বিষয়গুলো এক জায়গায় সাজানো হয়েছে।</p></div><div className="result-actions"><button className="secondary-button" onClick={downloadMarkdown}><ArrowDownToLine size={15} /> Export .md</button><button className="primary-button" onClick={() => setActiveTab('flashcards')}><Play size={15} /> Start review</button></div></div>
            <div className="topic-banner"><div className="topic-icon"><Lightbulb size={22} /></div><div><small>DETECTED TOPIC</small><h3>{result.title}</h3><span>{result.summary.slice(0, 92)}{result.summary.length > 92 ? '…' : ''}</span></div><div className="confidence"><span>Confidence</span><b>{result.confidence}%</b><div className="confidence-bar"><i style={{ width: `${result.confidence}%` }} /></div></div></div>
            <div className="content-tabs"><button className={activeTab === 'guide' ? 'tab active' : 'tab'} onClick={() => setActiveTab('guide')}><FileText size={16} /> Study guide</button><button className={activeTab === 'flashcards' ? 'tab active' : 'tab'} onClick={() => setActiveTab('flashcards')}><BrainCircuit size={16} /> Flashcards <span>{result.flashcards.length}</span></button><button className={activeTab === 'code' ? 'tab active' : 'tab'} onClick={() => setActiveTab('code')}><Code2 size={16} /> Code extracted <span>{result.code.length}</span></button></div>
            {activeTab === 'guide' && <Guide result={result} onCopy={() => { navigator.clipboard?.writeText(result.summary); setToast('Summary copied হয়েছে।'); }} />}
            {activeTab === 'flashcards' && <Flashcards cards={result.flashcards} />}
            {activeTab === 'code' && <CodeSnippets snippets={result.code} onCopy={() => setToast('Code copied হয়েছে।')} />}
          </section>}
          {!result && !isProcessing && <div className="empty-hint"><div><Sparkles size={17} /><b>AI কী কী বুঝতে পারে?</b><span>Heading, paragraph, bullet, diagram labels, code এবং formula</span></div><ArrowDownToLine size={16} /></div>}
        </div>
        <footer><span>Made for curious learners in Bangladesh</span><span>Board2Learn BD <i>•</i> v1.0</span></footer>
      </main>
      {toast && <div className="toast"><Check size={16} /> {toast}</div>}
    </div>
  );
}

function Guide({ result, onCopy }) {
  return <div className="guide-grid"><article className="summary-card"><div className="card-kicker"><span className="kicker-icon"><MessageSquareText size={15} /></span><span>সহজ বাংলায়</span><button className="icon-button" onClick={onCopy} aria-label="Copy summary"><Copy size={15} /></button></div><p className="summary-text">{result.summary}</p><div className="language-pills">{result.languages.map((language) => <span key={language}>{language}</span>)}</div></article><article className="concept-card"><div className="card-title"><div><h3>মূল ধারণাগুলো</h3><p>Board থেকে পাওয়া concepts</p></div><span className="concept-count">{result.headings.length} topics</span></div><div className="concept-list">{result.headings.map((item, index) => <div className="concept-row" key={`${item.title}-${index}`}><span className="concept-number">{String(index + 1).padStart(2, '0')}</span><div><b>{item.title}</b><p>{item.description}</p></div><ArrowUpRight size={15} /></div>)}</div></article><article className="bullet-card"><div className="card-title"><div><h3>দ্রুত মনে রাখুন</h3><p>Key takeaways</p></div><Zap size={18} /></div><ul>{result.bullets.map((item, index) => <li key={`${item}-${index}`}><span>✓</span>{item}</li>)}</ul></article><article className="unclear-card"><div className="unclear-mark">?</div><div><h3>একটু অস্পষ্ট</h3><p>এই অংশগুলো original board থেকে আবার দেখে নিন</p>{result.unclear.map((item, index) => <span key={`${item}-${index}`}>↳ {item}</span>)}</div></article></div>;
}

function Flashcards({ cards }) {
  const [revealed, setRevealed] = useState({});
  if (!cards.length) return <div className="no-code"><BrainCircuit size={24} /><h3>ফ্ল্যাশকার্ড তৈরি করা যায়নি</h3><p>এই ছবিতে পর্যাপ্ত পাঠযোগ্য লেখা পাওয়া যায়নি।</p></div>;
  return <div className="flashcards-grid">{cards.map((card, index) => <button className={revealed[index] ? 'flashcard revealed' : 'flashcard'} key={`${card.question}-${index}`} onClick={() => setRevealed((old) => ({ ...old, [index]: !old[index] }))}><div className="flashcard-top"><span>{String(index + 1).padStart(2, '0')}</span><span>{revealed[index] ? 'ANSWER' : 'QUESTION'}</span></div><strong>{revealed[index] ? card.answer : card.question}</strong><small>{revealed[index] ? 'উত্তর লুকাতে click করুন' : 'উত্তর দেখতে click করুন'}</small></button>)}</div>;
}

function CodeSnippets({ snippets, onCopy }) {
  if (!snippets.length) return <div className="no-code"><Code2 size={24} /><h3>কোনো code পাওয়া যায়নি</h3><p>এই board-এ formatted code বা pseudocode detect করা যায়নি।</p></div>;
  return <div className="code-list">{snippets.map((snippet, index) => <article className="code-card" key={`${snippet.title}-${index}`}><div className="code-header"><div><Code2 size={16} /><b>{snippet.title}</b></div><div><span>{snippet.language}</span><button className="icon-button" onClick={() => { navigator.clipboard?.writeText(snippet.code); onCopy(); }} aria-label="Copy code"><Copy size={15} /></button></div></div><pre><code>{snippet.code}</code></pre></article>)}</div>;
}

export default App;
