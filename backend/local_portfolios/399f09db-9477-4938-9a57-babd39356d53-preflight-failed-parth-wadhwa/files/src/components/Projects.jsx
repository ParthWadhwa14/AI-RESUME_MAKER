import React from 'react';
import { motion } from 'framer-motion';
import ProjectCard from './ProjectCard';

const projects = [
 {
 title: 'Agentic RAG System',
 pitch: 'Engineered an advanced Retrieval-Augmented Generation (RAG) system utilizing LangGraph to design complex, stateful multi-turn agentic loops',
 highlights: [
 'Utilized LangGraph for advanced RAG system design',
 'Implemented stateful multi-turn agentic loops',
 'Integrated with OpenAI SDK and ChromaDB',
 ],
 techStack: ['LangGraph', 'Python', 'OpenAI SDK', 'ChromaDB'],
 },
 {
 title: 'ResearchSync - AI-Powered Research Collaboration Platform',
 pitch: 'Built a full-stack collaborative platform with real-time chat, Kanban task management, and shared research workspaces',
 highlights: [
 'Developed a full-stack platform using React and Node.js',
 'Implemented real-time chat and Kanban task management',
 'Integrated with Supabase and Gemini API',
 ],
 techStack: ['React', 'Node.js', 'Supabase', 'Gemini API'],
 },
 {
 title: 'Network Intrusion Detection System',
 pitch: 'Designed an ML pipeline for malicious traffic detection using preprocessing, feature engineering, and supervised learning',
 highlights: [
 'Developed an ML pipeline using Python and scikit-learn',
 'Implemented preprocessing, feature engineering, and supervised learning',
 'Detected malicious traffic with high accuracy',
 ],
 techStack: ['Python', 'scikit-learn'],
 },
 {
 title: 'SehatSaathi-AI',
 pitch: 'Built an AI-powered healthcare assistance platform providing symptom-based guidance, medical information, and intelligent conversational support',
 highlights: [
 'Developed an AI-powered platform using React and Node.js',
 'Implemented symptom-based guidance and medical information',
 'Integrated with AI APIs',
 ],
 techStack: ['React', 'Node.js', 'AI APIs'],
 },
 {
 title: 'Mental-Health-AI-Copilot',
 pitch: 'Developed an AI-driven mental health support assistant capable of empathetic conversations, personalized guidance, and wellness-focused interactions',
 highlights: [
 'Developed an AI-driven assistant using React and Node.js',
 'Implemented empathetic conversations and personalized guidance',
 'Integrated with Generative AI',
 ],
 techStack: ['React', 'Node.js', 'Generative AI'],
 },
];

const Projects = () => {
 return (
 <section className="projects">
 <h2>Projects</h2>
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 {projects.map((project, index) => (
 <ProjectCard key={index} project={project} />
 ))}
 </motion.div>
 </section>
 );
};

export default Projects;
