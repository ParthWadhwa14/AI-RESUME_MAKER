import React from 'react';
import { motion } from 'framer-motion';
import { AiOutlineCode } from 'lucide-react';

const SkillCard = ({ skill }) => {
 return (
 <motion.div
 initial={{ opacity: 0, y: 20 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ duration: 0.3 }}
 className="skill-card"
 >
 <h3>{skill.name}</h3>
 <p>{skill.proficiency}</p>
 <AiOutlineCode size={24} />
 </motion.div>
 );
};

export default SkillCard;
