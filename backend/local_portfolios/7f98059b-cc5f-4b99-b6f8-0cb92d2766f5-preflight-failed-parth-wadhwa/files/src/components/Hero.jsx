import React from 'react';
import { motion } from 'framer-motion';
import { FiArrowDown } from 'lucide-react';

export default function Hero() {
 return (
 <section className="hero">
 <motion.h1
 initial={{ opacity: 0, y: -50 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ duration: 0.5 }}
 >
 Parth Wadhwa
 </motion.h1>
 <motion.p
 initial={{ opacity: 0, y: -50 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ duration: 0.5, delay: 0.2 }}
 >
 B.Tech Chemical Engineering Student and AI Enthusiast
 </motion.p>
 <motion.button
 initial={{ opacity: 0, y: -50 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ duration: 0.5, delay: 0.4 }}
 className="cta"
 >
 Explore my portfolio <FiArrowDown />
 </motion.button>
 </section>
 );
}
