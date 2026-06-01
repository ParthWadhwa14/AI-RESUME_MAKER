import React from 'react';
import { motion } from 'framer-motion';
import ProjectCard from './ProjectCard';

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

export default function Projects() {
 return (
 <section className="projects bg-gray-800 text-white p-4 flex flex-col items-center justify-center">
 <h2 className="text-3xl">Projects</h2>
 <motion.div className="project-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" initial="hidden" whileInView="visible" viewport={{ once: true }}>
 {projects.map((project, index) => (
 <ProjectCard key={index} project={project} />
 ))}
 </motion.div>
 </section>
 );
}