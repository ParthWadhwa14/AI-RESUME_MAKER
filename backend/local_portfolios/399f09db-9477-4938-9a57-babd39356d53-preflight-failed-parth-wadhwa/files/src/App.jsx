import React from 'react';
import { motion } from 'framer-motion';
import Hero from './components/Hero';
import Projects from './components/Projects';
import Skills from './components/Skills';
import Contact from './components/Contact';

const App = () => {
 return (
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 <Hero />
 <Projects />
 <Skills />
 <Contact />
 </motion.div>
 );
};

export default App;
