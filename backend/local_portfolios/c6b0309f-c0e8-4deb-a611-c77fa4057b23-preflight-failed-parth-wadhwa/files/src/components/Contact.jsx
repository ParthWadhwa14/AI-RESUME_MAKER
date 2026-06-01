import React from 'react';
import { motion } from 'framer-motion';

const Contact = () => {
 return (
 <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }} className="bg-white p-4 shadow-md">
 <h2 className="text-3xl font-bold">Get in Touch</h2>
 <p className="text-lg">Email: <a href="mailto:parthwadhwa@example.com" className="text-blue-600 hover:text-blue-800">parthwadhwa@example.com</a></p>
 <p className="text-lg">LinkedIn: <a href="https://www.linkedin.com/in/parth-wadhwa-855650323" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">https://www.linkedin.com/in/parth-wadhwa-855650323</a></p>
 </motion.section>
 );
};

export default Contact;
