import React from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import Hero from './components/Hero';
import Projects from './components/Projects';
import Skills from './components/Skills';
import Experience from './components/Experience';

export default function App() {
 return (
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.5 }}
 >
 <Header />
 <Hero />
 <Projects />
 <Skills />
 <Experience />
 </motion.div>
 );
}
