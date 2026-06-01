import React from 'react';
import { motion } from 'framer-motion';

export default function Hero() {
 return (
 <section className="hero">
 <motion.h1 initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3, ease: 'easeInOut' }}>
 Parth Wadhwa
 </motion.h1>
 <motion.p initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3, ease: 'easeInOut' }}>
 B.Tech Chemical Engineering
 </motion.p>
 <motion.button initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3, ease: 'easeInOut' }} className="bg-primary text-light hover:bg-secondary hover:text-dark rounded-md py-2 px-4">
 Explore My Portfolio
 </motion.button>
 </section>
 );
}