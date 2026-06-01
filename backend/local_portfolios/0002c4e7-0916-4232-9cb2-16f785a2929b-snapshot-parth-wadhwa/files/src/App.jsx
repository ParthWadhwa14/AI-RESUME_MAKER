import React from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import Projects from './components/Projects';
import Skills from './components/Skills';
import Education from './components/Education';

function App() {
 return (
 <main className="app-shell">
 <Header />
 <motion.section initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ duration: 0.3 }} className="section">
 <h2>Experience</h2>
 <p>AI Intern with experience in computer vision and machine learning.</p>
 </motion.section>
 <Projects />
 <Skills />
 <Education />
 </main>
 );
}

export default App;