import React from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import Experience from './components/Experience';
import Projects from './components/Projects';
import Skills from './components/Skills';
import Contact from './components/Contact';

const App = () => {
 return (
 <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
 <Header />
 <Experience />
 <Projects />
 <Skills />
 <Contact />
 </motion.div>
 );
};

export default App;
