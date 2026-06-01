import React from 'react';
import { motion } from 'framer-motion';
import { FiGitlab } from 'lucide-react';

export default function Projects() {
 return (
 <section className="projects">
 <h2>Projects</h2>
 <ul>
 <li>
 <motion.div
 whileHover={{ scale: 1.1 }}
 transition={{ duration: 0.2 }}
 className="project-card"
 >
 <h3>Agentic RAG System</h3>
 <p>Engineered an advanced Retrieval-Augmented Generation (RAG) system utilizing LangGraph to design complex, stateful multi-turn agentic loops.</p>
 <ul>
 <li>Implemented semantic document parsing, recursive text splitting, and vector embeddings to extract and index data from custom enterprise knowledge bases.</li>
 <li>Designed fallback execution routers and self-correction reflection nodes that dynamically evaluate document relevance and self-correct hallucinations before output generation.</li>
 </ul>
 <div className="tech-stack">
 <FiGitlab size={20} />
 LangGraph
 </div>
 </motion.div>
 </li>
 </ul>
 </section>
 );
}
