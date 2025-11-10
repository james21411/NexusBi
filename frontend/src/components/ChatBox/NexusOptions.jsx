import React from "react";

import "./NexusOptions.css";

//options component that will guide the user to possible BI options.

const NexusOptions = (props) => {
    const options = [
        {
            text : "Sales Analysis",
            handler: props.actionProvider.handleSalesAnalysis,
            id:1,
        },
        {
            text : "Customer Insights",
            handler:props.actionProvider.handleCustomerInsights,
            id:2,
        },
        {
            text : "Performance Metrics",
            handler:props.actionProvider.handlePerformanceMetrics,
            id:3,
        },
        {
            text : "Data Visualization",
            handler:props.actionProvider.handleDataVisualization,
            id:4,
        },
        {
            text : "Custom Query",
            handler:props.actionProvider.handleCustomQuery,
            id:5,
        },
    ];


    const optionsMarkup = options.map((option) => (
        <button
        className="nexus-option-button"
        key={option.id}
        onClick={option.handler}>
            {option.text}
        </button>
    ));

    return <div className="nexus-options-container">{optionsMarkup}</div>
};

export default NexusOptions;