import React from 'react';
import { motion } from 'framer-motion';
import { FiGithub } from 'lucide-react';
import Projects from './Projects';
import Skills from './Skills';
import Hero from './Hero';

export default function App() {
 return (
 <main className="app-shell">
 <Hero />
 <Projects />
 <Skills />
 </main>
 );
}