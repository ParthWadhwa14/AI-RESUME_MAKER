import React from 'react';
import { motion } from 'framer-motion';
import ProjectCard from './ProjectCard';

function Projects() {
 const projects = [
 {
 title: 'Agentic RAG System',
 pitch: 'Engineered an advanced Retrieval-Augmented Generation (RAG) system utilizing LangGraph to design complex, stateful multi-turn agentic loops.',
 highlights: [
 'Implemented semantic document parsing, recursive text splitting, and vector embeddings to extract and index data from custom enterprise knowledge bases.',
 'Designed fallback execution routers and self-correction reflection nodes that dynamically evaluate document relevance and self-correct hallucinations before output generation.',
 ],
 techStack: ['LangGraph', 'Python', 'OpenAI SDK', 'ChromaDB'],
 },
 ];

 return (
 <motion.section initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ duration: 0.3 }} className="section">
 <h2>Projects</h2>
 <div className="projects-grid">
 {projects.map((project, index) => (
 <ProjectCard key={index} project={project} />
 ))}
 </div>
 </motion.section>
 );
}

export default Projects;