import React from 'react';
import { motion } from 'framer-motion';
import { Github } from 'lucide-react';

export default function ProjectCard({ project }) {
 return (
 <motion.div className="project-card bg-gray-900 text-white p-4 rounded-lg shadow-lg hover:scale-105" whileHover={{ scale: 1.05 }}>
 <h3 className="text-xl">{project.title}</h3>
 <p className="text-lg">{project.pitch}</p>
 <ul>
 {project.highlights.map((highlight, index) => (
 <li key={index} className="text-lg">{highlight}</li>
 ))}
 </ul>
 <div className="tech-stack flex justify-center">
 {project.techStack.map((tech, index) => (
 <span key={index} className="text-lg">{tech}</span>
 ))}
 </div>
 <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-blue-500">
 <Github size={24} />
 </a>
 </motion.div>
 );
}