import React from 'react';
import { motion } from 'framer-motion';
import ProjectCard from './ProjectCard';

const projects = [
 {
 name: 'Agentic RAG System',
 pitch: 'Engineered an advanced Retrieval-Augmented Generation (RAG) system utilizing LangGraph to design complex, stateful multi-turn agentic loops',
 highlights: [
 'Utilized LangGraph for complex stateful multi-turn agentic loops',
 'Designed advanced Retrieval-Augmented Generation (RAG) system',
 'Implemented using Python, OpenAI SDK, and ChromaDB',
 ],
 techStack: ['LangGraph', 'Python', 'OpenAI SDK', 'ChromaDB'],
 },
 {
 name: 'ResearchSync - AI-Powered Research Collaboration Platform',
 pitch: 'Built a full-stack collaborative platform with real-time chat, Kanban task management, and shared research workspaces',
 highlights: [
 'Developed full-stack platform using React, Node.js, Supabase, and Gemini API',
 'Implemented real-time chat and Kanban task management',
 'Enabled shared research workspaces for collaboration',
 ],
 techStack: ['React', 'Node.js', 'Supabase', 'Gemini API'],
 },
 {
 name: 'Network Intrusion Detection System',
 pitch: 'Designed an ML pipeline for malicious traffic detection using preprocessing, feature engineering, and supervised learning',
 highlights: [
 'Developed ML pipeline for malicious traffic detection',
 'Utilized preprocessing, feature engineering, and supervised learning',
 'Implemented using Python and scikit-learn',
 ],
 techStack: ['Python', 'scikit-learn'],
 },
 {
 name: 'SehatSaathi-AI',
 pitch: 'Built an AI-powered healthcare assistance platform providing symptom-based guidance, medical information, and intelligent conversational support',
 highlights: [
 'Developed AI-powered healthcare assistance platform',
 'Provided symptom-based guidance and medical information',
 'Implemented intelligent conversational support using React, Node.js, and AI APIs',
 ],
 techStack: ['React', 'Node.js', 'AI APIs'],
 },
 {
 name: 'Mental-Health-AI-Copilot',
 pitch: 'Developed an AI-driven mental health support assistant capable of empathetic conversations, personalized guidance, and wellness-focused interactions',
 highlights: [
 'Developed AI-driven mental health support assistant',
 'Enabled empathetic conversations and personalized guidance',
 'Implemented using React, Node.js, and Generative AI',
 ],
 techStack: ['React', 'Node.js', 'Generative AI'],
 },
];

export default function Projects() {
 return (
 <section className="projects bg-gray-800 p-4 text-white">
 <h2 className="text-3xl font-bold mb-4">Projects</h2>
 <motion.div layout>
 {projects.map((project, index) => (
 <ProjectCard key={index} project={project} />
 ))}
 </motion.div>
 </section>
 );
}