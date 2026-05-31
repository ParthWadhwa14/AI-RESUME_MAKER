import React from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import Projects from './components/Projects';
import Skills from './components/Skills';
import Education from './components/Education';

export default function App() {
 return (
 <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
 <Header />
 <Projects />
 <Skills />
 <Education />
 </motion.div>
 );
}