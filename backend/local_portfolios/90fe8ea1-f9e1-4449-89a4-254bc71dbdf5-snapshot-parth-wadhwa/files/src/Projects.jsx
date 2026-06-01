import React from 'react';
import { motion } from 'framer-motion';
import { FiGithub } from 'lucide-react';

export default function Projects() {
 const projects = [
 {
 name: 'Agentic RAG System',
 pitch: 'Engineered an advanced Retrieval-Augmented Generation (RAG) system utilizing LangGraph',
 highlights: [
 'Implemented semantic document parsing, recursive text splitting, and vector embeddings',
 'Designed fallback execution routers and self-correction reflection nodes',
 'Utilized LangGraph, Python, OpenAI SDK, and ChromaDB'
 ],
 techStack: ['LangGraph', 'Python', 'OpenAI SDK', 'ChromaDB'],
 outcomes: []
 }
 ];

 return (
 <section className="projects">
 {projects.map((project, index) => (
 <motion.div key={index} initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3, ease: 'easeInOut' }} className="bg-glass shadow-md rounded-lg p-4">
 <h2>{project.name}</h2>
 <p>{project.pitch}</p>
 <ul>
 {project.highlights.map((highlight, index) => (
 <li key={index}>{highlight}</li>
 ))}
 </ul>
 <div className="tech-stack">
 {project.techStack.map((tech, index) => (
 <span key={index} className="bg-primary text-light rounded-md py-2 px-4">
 {tech}
 </span>
 ))}
 </div>
 </motion.div>
 ))}
 </section>
 );
}