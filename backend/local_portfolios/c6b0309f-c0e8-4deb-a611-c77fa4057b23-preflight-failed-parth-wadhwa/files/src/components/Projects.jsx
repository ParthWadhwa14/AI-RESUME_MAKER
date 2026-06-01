import React from 'react';
import { motion } from 'framer-motion';
import { AiOutlineGithub, AiOutlineLink } from 'lucide-react';

const Projects = () => {
 const projects = [
 {
 name: 'Agentic RAG System',
 pitch: 'Engineered an advanced Retrieval-Augmented Generation (RAG) system utilizing LangGraph to design complex, stateful multi-turn agentic loops.',
 highlights: [
 'Implemented semantic document parsing, recursive text splitting, and vector embeddings to extract and index data from custom enterprise knowledge bases.',
 'Designed fallback execution routers and self-correction reflection nodes that dynamically evaluate document relevance and self-correct hallucinations before output generation.',
 ],
 techStack: ['LangGraph', 'Python', 'OpenAI SDK', 'ChromaDB'],
 outcomes: [],
 },
 ];

 return (
 <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }} className="bg-white p-4 shadow-md">
 <h2 className="text-3xl font-bold">Projects</h2>
 <ul>
 {projects.map((project, index) => (
 <li key={index} className="mb-4">
 <h3 className="text-2xl font-bold">{project.name}</h3>
 <p className="text-xl">{project.pitch}</p>
 <ul>
 {project.highlights.map((highlight, index) => (
 <li key={index} className="text-lg">{highlight}</li>
 ))}
 </ul>
 <ul className="tech-stack flex flex-wrap justify-center items-center">
 {project.techStack.map((tech, index) => (
 <li key={index} className="bg-gray-200 p-2 m-2 rounded-md">{tech}</li>
 ))}
 </ul>
 <ul className="outcomes">
 {project.outcomes.map((outcome, index) => (
 <li key={index} className="text-lg">{outcome}</li>
 ))}
 </ul>
 <a href="https://github.com/parthwadhwa/agentic-rag-system" target="_blank" rel="noopener noreferrer" className="text-white hover:text-gray-300">
 <AiOutlineGithub size={24} />
 </a>
 </li>
 ))}
 </ul>
 </motion.section>
 );
};

export default Projects;
