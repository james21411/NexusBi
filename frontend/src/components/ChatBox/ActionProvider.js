import config from "./config";

// ActionProvider for NexusBI chatbot
class ActionProvider {
    constructor(createChatBotMessage, setStateFunc, createClientMessage) {
      this.createChatBotMessage = createChatBotMessage;
      this.setState = setStateFunc;
      this.createClientMessage = createClientMessage;
    }

    // Handle sales analysis queries
    handleSalesAnalysis = () => {
        const message = this.createChatBotMessage(
            "Great! I can help you analyze sales data. What would you like to know?",
            {
                widget: "salesOptions",
            }
        );
        this.updateChatbotState(message);
    };

    // Handle customer insights
    handleCustomerInsights = () => {
        const message = this.createChatBotMessage(
            "Customer insights are crucial for business growth. What aspect interests you?",
            {
                widget: "customerOptions",
            }
        );
        this.updateChatbotState(message);
    };

    // Handle performance metrics
    handlePerformanceMetrics = () => {
        const message = this.createChatBotMessage(
            "Let's look at your key performance indicators. Choose a metric:",
            {
                widget: "performanceOptions",
            }
        );
        this.updateChatbotState(message);
    };

    // Handle data visualization
    handleDataVisualization = () => {
        const message = this.createChatBotMessage(
            "Data visualization helps understand complex data. What type of chart would you like?",
            {
                widget: "visualizationOptions",
            }
        );
        this.updateChatbotState(message);
    };

    // Handle custom queries
    handleCustomQuery = () => {
        const message = this.createChatBotMessage(
            "Feel free to ask me any question about your data in natural language. I'm here to help!"
        );
        this.updateChatbotState(message);
    };

    // Process natural language queries
    handleQuery = async (query) => {
        // Show processing message
        const processingMessage = this.createChatBotMessage("Analyzing your query...");
        this.updateChatbotState(processingMessage);

        try {
            // Here you would integrate with your backend API
            // For now, we'll simulate a response
            const response = await this.simulateAPIResponse(query);

            const resultMessage = this.createChatBotMessage(response, {
                widget: "dataWidget",
                props: { data: response }
            });
            this.updateChatbotState(resultMessage);
        } catch (error) {
            const errorMessage = this.createChatBotMessage(
                "I apologize, but I encountered an error processing your request. Please try again."
            );
            this.updateChatbotState(errorMessage);
        }
    };

    // Simulate API response (replace with actual API call)
    simulateAPIResponse = async (query) => {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Simple keyword-based responses
        const lowerQuery = query.toLowerCase();

        if (lowerQuery.includes('sales') && lowerQuery.includes('total')) {
            return "Based on your data, the total sales for this period is $1,245,678. This represents a 12% increase from the previous period.";
        } else if (lowerQuery.includes('top') && lowerQuery.includes('product')) {
            return "Your top-selling products are:\n1. Product A - $234,567\n2. Product B - $198,432\n3. Product C - $156,789";
        } else if (lowerQuery.includes('revenue') && lowerQuery.includes('month')) {
            return "Monthly revenue breakdown:\n- January: $145,678\n- February: $167,890\n- March: $189,234\n- April: $201,456";
        } else {
            return "I've processed your query: '" + query + "'. In a full implementation, this would connect to your data source and provide relevant insights.";
        }
    };

    // Greeting
    greet = () => {
        const greetingMessage = this.createChatBotMessage("Hello! I'm NexusBI, your intelligent business intelligence assistant. How can I help you analyze your data today?", {
            widget: "nexusOptions",
        });
        this.updateChatbotState(greetingMessage);
    };

    // Farewell
    farewell = () => {
        const farewellMessage = this.createChatBotMessage(
            "Thank you for using NexusBI! Feel free to come back anytime for data insights.",
            {
                end: true,
            }
        );
        this.updateChatbotState(farewellMessage);
    };

    updateChatbotState(message) {
        this.setState(prevState => ({
            ...prevState, messages: [...prevState.messages, message]
        }));
    }
}

export default ActionProvider;