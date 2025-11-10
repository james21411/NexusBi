// MessageParser for NexusBI chatbot
class MessageParser {
    constructor(actionProvider, state) {
      this.actionProvider = actionProvider;
      this.state = state;
    }

    parse(message) {
        const lowerCaseMessage = message.toLowerCase();

        // Greeting patterns
        if (this.isGreeting(lowerCaseMessage)) {
            this.actionProvider.greet();
            return;
        }

        // Farewell patterns
        if (this.isFarewell(lowerCaseMessage)) {
            this.actionProvider.farewell();
            return;
        }

        // BI-specific queries
        if (this.isSalesQuery(lowerCaseMessage)) {
            this.actionProvider.handleSalesAnalysis();
            return;
        }

        if (this.isCustomerQuery(lowerCaseMessage)) {
            this.actionProvider.handleCustomerInsights();
            return;
        }

        if (this.isPerformanceQuery(lowerCaseMessage)) {
            this.actionProvider.handlePerformanceMetrics();
            return;
        }

        if (this.isVisualizationQuery(lowerCaseMessage)) {
            this.actionProvider.handleDataVisualization();
            return;
        }

        // Default: treat as natural language query
        this.actionProvider.handleQuery(message);
    }

    isGreeting(message) {
        const greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings'];
        return greetings.some(greeting => message.includes(greeting));
    }

    isFarewell(message) {
        const farewells = ['bye', 'goodbye', 'see you', 'farewell', 'take care', 'thanks', 'thank you'];
        return farewells.some(farewell => message.includes(farewell));
    }

    isSalesQuery(message) {
        const salesKeywords = ['sales', 'revenue', 'income', 'profit', 'turnover', 'earnings'];
        return salesKeywords.some(keyword => message.includes(keyword));
    }

    isCustomerQuery(message) {
        const customerKeywords = ['customer', 'client', 'user', 'buyer', 'consumer', 'segment'];
        return customerKeywords.some(keyword => message.includes(keyword));
    }

    isPerformanceQuery(message) {
        const performanceKeywords = ['performance', 'kpi', 'metric', 'indicator', 'efficiency', 'productivity'];
        return performanceKeywords.some(keyword => message.includes(keyword));
    }

    isVisualizationQuery(message) {
        const visualizationKeywords = ['chart', 'graph', 'visual', 'plot', 'diagram', 'dashboard'];
        return visualizationKeywords.some(keyword => message.includes(keyword));
    }
}

export default MessageParser;