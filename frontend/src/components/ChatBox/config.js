import React from "react";
import { createChatBotMessage } from "react-chatbot-kit";
import NexusOptions from "./NexusOptions";
import BotAvatar from "./BotAvatar";

const config = {
    botName: "NexusBI",
    initialMessages: [
        createChatBotMessage("Hello! I'm NexusBI, your intelligent business intelligence assistant.", {
            widget: "nexusOptions",
        }),
    ],
    customComponents: {
        botAvatar: (props) => <BotAvatar {...props} />,
    },
    customStyles: {
        botMessageBox: {
            backgroundColor: '#3b82f6',
        },
        chatButton: {
            backgroundColor: '#3b82f6',
        },
    },
    state: {},
    widgets: [
        {
            widgetName: "nexusOptions",
            widgetFunc: (props) => <NexusOptions {...props} />,
        },
        {
            widgetName: "salesOptions",
            widgetFunc: (props) => (
                <div className="nexus-options-container">
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Show total sales")}>
                        Total Sales
                    </button>
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Sales by region")}>
                        Sales by Region
                    </button>
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Top products")}>
                        Top Products
                    </button>
                </div>
            ),
        },
        {
            widgetName: "customerOptions",
            widgetFunc: (props) => (
                <div className="nexus-options-container">
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Customer segments")}>
                        Customer Segments
                    </button>
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Customer lifetime value")}>
                        Lifetime Value
                    </button>
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Customer retention")}>
                        Retention Rate
                    </button>
                </div>
            ),
        },
        {
            widgetName: "performanceOptions",
            widgetFunc: (props) => (
                <div className="nexus-options-container">
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("KPI dashboard")}>
                        KPI Dashboard
                    </button>
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Conversion rates")}>
                        Conversion Rates
                    </button>
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Growth metrics")}>
                        Growth Metrics
                    </button>
                </div>
            ),
        },
        {
            widgetName: "visualizationOptions",
            widgetFunc: (props) => (
                <div className="nexus-options-container">
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Create bar chart")}>
                        Bar Chart
                    </button>
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Create line chart")}>
                        Line Chart
                    </button>
                    <button className="nexus-option-button" onClick={() => props.actionProvider.handleQuery("Create pie chart")}>
                        Pie Chart
                    </button>
                </div>
            ),
        },
        {
            widgetName: "dataWidget",
            widgetFunc: (props) => (
                <div style={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    padding: '10px',
                    borderRadius: '5px',
                    margin: '10px 0',
                    whiteSpace: 'pre-line'
                }}>
                    <strong>Data Result:</strong><br />
                    {props.data}
                </div>
            ),
        },
    ],
};

export default config;