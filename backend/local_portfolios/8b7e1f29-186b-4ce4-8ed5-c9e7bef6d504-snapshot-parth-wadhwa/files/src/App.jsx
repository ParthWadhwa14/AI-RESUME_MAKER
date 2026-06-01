import React from 'react';
import { motion } from 'framer-motion';
import Hero from './components/Hero';
import About from './components/About';
import Experience from './components/Experience';
import Projects from './components/Projects';
import Skills from './components/Skills';
import Contact from './components/Contact';

export default function App() {
 return (
 <main className="app-shell">
 <Hero />
 <About />
 <Experience />
 <Projects />
 <Skills />
 <Contact />
 </main>
 );
}
