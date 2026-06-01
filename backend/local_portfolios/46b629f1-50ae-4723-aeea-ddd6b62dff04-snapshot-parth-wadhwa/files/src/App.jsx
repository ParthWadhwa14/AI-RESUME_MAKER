import React from 'react';
import { motion } from 'framer-motion';
import { Home } from './Home';
import { ExperienceTimeline } from './ExperienceTimeline';
import { BentoProjects } from './BentoProjects';
import { SkillsMatrix } from './SkillsMatrix';
import { ContactForm } from './ContactForm';
import { Route, Routes, BrowserRouter } from 'react-router-dom';

export default function App() {
 return (
 <BrowserRouter>
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 <Routes>
 <Route path="/" element={<Home />} />
 <Route path="/experience" element={<ExperienceTimeline />} />
 <Route path="/projects" element={<BentoProjects />} />
 <Route path="/skills" element={<SkillsMatrix />} />
 <Route path="/contact" element={<ContactForm />} />
 </Routes>
 </motion.div>
 </BrowserRouter>
 );
}