import React from 'react';
import { motion } from 'framer-motion';
import { AiOutlineCode } from 'lucide-react';

const ProjectCard = ({ project }) => {
 return (
 <motion.div
 initial={{ opacity: 0, y: 20 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ duration: 0.3 }}
 className="project-card"
 >
 <h3>{project.title}</h3>
 <p>{project.pitch}</p>
 <ul>
 {project.highlights.map((highlight, index) => (
 <li key={index}>{highlight}</li>
 ))}
 </ul>
 <div className="tech-stack">
 {project.techStack.map((tech, index) => (
 <span key={index}>{tech}</span>
 ))}
 </div>
 <a href="#" target="_blank" rel="noopener noreferrer">
 <AiOutlineCode size={24} />
 </a>
 </motion.div>
 );
};

export default ProjectCard;
