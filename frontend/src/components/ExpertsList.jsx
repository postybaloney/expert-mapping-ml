import React, { useEffect, useState } from 'react';
import { fetchExperts } from '../api';

const ExpertsList = () => {
    const [experts, setExperts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getExperts = async () => {
            try {
                const data = await fetchExperts();
                setExperts(data.experts);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        getExperts();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div>
            <h2>Experts List</h2>
            <ul>
                {experts.map((expert) => (
                    <li key={expert.username}>
                        <h3>{expert.username}</h3>
                        <p>{expert.expertise}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ExpertsList;