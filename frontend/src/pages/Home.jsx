import React from 'react';
import ExpertsList from '../components/ExpertsList';

const Home = () => {
    return (
        <div>
            <h1>Welcome to the Experts Directory</h1>
            <p>Find the best experts for your needs.</p>
            <ExpertsList />
        </div>
    );
};

export default Home;