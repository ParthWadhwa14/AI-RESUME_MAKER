import React from 'react';
import Header from './components/Header';
import Projects from './components/Projects';
import Skills from './components/Skills';
import Experience from './components/Experience';
import Education from './components/Education';

export default function App() {
 return (
 <main className="app-shell flex flex-col items-center justify-center h-screen">
 <Header />
 <Projects />
 <Skills />
 <Experience />
 <Education />
 </main>
 );
}