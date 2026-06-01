import React from 'react';
import { motion } from 'framer-motion';
import ProjectCard from './ProjectCard';

const projects = [
 {
 title: 'Agentic RAG System',
 pitch: 'Engineered an advanced Retrieval-Augmented Generation (RAG) system utilizing LangGraph',
 highlights: [
 'Utilized LangGraph for advanced text generation',
 'Integrated with OpenAI SDK for enhanced capabilities',
 'Built with Python and ChromaDB for efficient data management',
 ],
 techStack: ['LangGraph', 'Python', 'OpenAI SDK', 'ChromaDB'],
 },
 {
 title: 'ResearchSync - AI-Powered Research Collaboration Platform',
 pitch: 'Built a full-stack collaborative platform with real-time chat, Kanban task management, and shared research workspaces',
 highlights: [
 'Developed with React and Node.js for a seamless user experience',
 'Integrated with Supabase for real-time data synchronization',
 'Utilized Gemini API for enhanced AI capabilities',
 ],
 techStack: ['React', 'Node.js', 'Supabase', 'Gemini API'],
 },
 {
 title: 'Network Intrusion Detection System',
 pitch: 'Designed an ML pipeline for malicious traffic detection using preprocessing, feature engineering, and supervised learning',
 highlights: [
 'Built with Python and scikit-learn for efficient ML model development',
 'Utilized preprocessing and feature engineering for enhanced data quality',
 'Trained with supervised learning for accurate traffic detection',
 ],
 techStack: ['Python', 'scikit-learn'],
 },
 {
 title: 'SehatSaathi-AI',
 pitch: 'Built an AI-powered healthcare assistance platform providing symptom-based guidance, medical information, and intelligent conversational support',
 highlights: [
 'Developed with React and Node.js for a seamless user experience',
 'Integrated with AI APIs for enhanced healthcare capabilities',
 'Utilized natural language processing for intelligent conversational support',
 ],
 techStack: ['React', 'Node.js', 'AI APIs'],
 },
 {
 title: 'Mental-Health-AI-Copilot',
 pitch: 'Developed an AI-driven mental health support assistant capable of empathetic conversations, personalized guidance, and wellness-focused interactions',
 highlights: [
 'Built with React and Node.js for a seamless user experience',
 'Integrated with Generative AI for enhanced mental health capabilities',
 'Utilized natural language processing for empathetic conversations',
 ],
 techStack: ['React', 'Node.js', 'Generative AI'],
 },
];

export default function Projects() {
 return (
 <section className="projects flex flex-col items-center py-4">
 <h1 className="text-3xl font-bold">Projects</h1>
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.5 }}
 >
 {projects.map((project, index) => (
 <ProjectCard key={index} project={project} />
 ))}
 </motion.div>
 </section>
 );
}
