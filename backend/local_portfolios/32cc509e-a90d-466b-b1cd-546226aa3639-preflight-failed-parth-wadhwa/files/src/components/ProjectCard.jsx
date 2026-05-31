import React from 'react';
import { motion } from 'framer-motion';
import { FiExternalLink } from 'react-icons/fi';

export default function ProjectCard({ project }) {
 return (
 <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className="bg-gray-700 p-4 rounded-md shadow-md mb-4">
 <div className="project-card">
 <h3 className="text-2xl font-bold mb-2">{project.name}</h3>
 <p className="text-xl mb-4">{project.pitch}</p>
 <ul>
 {project.highlights.map((highlight, index) => (
 <li key={index} className="text-lg mb-2">{highlight}</li>
 ))}
 </ul>
 <div className="tech-stack flex justify-start items-center space-x-2">
 {project.techStack.map((tech, index) => (
 <span key={index} className="text-lg bg-gray-600 p-2 rounded-md">{tech}</span>
 ))}
 </div>
 <a href="#" target="_blank" rel="noreferrer" className="hover:text-gray-300">
 <FiExternalLink size={24} />
 </a>
 </div>
 </motion.div>
 );
}