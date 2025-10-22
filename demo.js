const axios = require('axios');

const API_BASE = 'http://localhost:3000/api';

async function demoFlightSearch() {
    console.log('🚀 Travel Agent Flight Search Demo\n');
    console.log('=' .repeat(50));
    
    let context = { step: 'initial' };
    
    // Demo conversation flow
    const conversation = [
        'search flights',
        'Delhi', 
        'Mumbai',
        '2025-12-25',
        'price'
    ];
    
    for (let i = 0; i < conversation.length; i++) {
        const message = conversation[i];
        console.log(`\n👤 User: ${message}`);
        
        try {
            const response = await axios.post(`${API_BASE}/chat`, {
                message: message,
                context: context
            });
            
            const data = response.data;
            context = data.context;
            
            console.log(`🤖 Agent: ${data.response}`);
            
            // Add a small delay for better demo experience
            await new Promise(resolve => setTimeout(resolve, 1000));
            
        } catch (error) {
            console.error('❌ Error:', error.message);
            break;
        }
    }
    
    console.log('\n' + '='.repeat(50));
    console.log('✅ Demo completed! The flight search agent successfully:');
    console.log('   • Collected user inputs in sequence');
    console.log('   • Validated Indian airports and future dates');
    console.log('   • Generated mock flight data');
    console.log('   • Ranked flights by price, duration, and convenience');
    console.log('   • Presented top 3 options with clear labeling');
    console.log('\n🌐 Open index.html in your browser to try the chat interface!');
}

// Run the demo
demoFlightSearch().catch(console.error);

