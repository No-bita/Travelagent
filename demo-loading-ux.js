const axios = require('axios');

const API_BASE = 'http://localhost:3000/api';

async function demonstrateLoadingUX() {
    console.log('🎬 Loading UX Demonstration\n');
    console.log('=' .repeat(60));
    
    console.log('This demo shows the different loading states in the chat interface:');
    console.log('\n1. 🔄 Regular Chat Loading');
    console.log('   - Simple typing indicator');
    console.log('   - "Searching for flights..." message');
    console.log('   - Used for: origin, destination, date input');
    
    console.log('\n2. 🔍 Flight Search Loading');
    console.log('   - Animated searching indicator');
    console.log('   - Rotating messages:');
    console.log('     • "🔍 Searching flights..."');
    console.log('     • "✈️ Finding best options..."');
    console.log('     • "💰 Comparing prices..."');
    console.log('     • "⏰ Checking schedules..."');
    console.log('     • "🎯 Ranking results..."');
    console.log('   - Used for: preference selection (price/time/convenience)');
    
    console.log('\n3. 🎯 Send Button Loading');
    console.log('   - Button shows spinning loader');
    console.log('   - Prevents multiple submissions');
    console.log('   - Visual feedback during API calls');
    
    console.log('\n' + '=' .repeat(60));
    console.log('🧪 Testing Loading States...\n');
    
    // Test regular chat flow
    console.log('📋 Regular Chat Flow:');
    console.log('-'.repeat(40));
    
    let context = { step: 'initial' };
    const regularSteps = [
        { message: "search flights", description: "Initial request" },
        { message: "Delhi", description: "Origin city" },
        { message: "Mumbai", description: "Destination city" },
        { message: "tomorrow", description: "Travel date" }
    ];
    
    for (const step of regularSteps) {
        try {
            console.log(`   💬 "${step.message}" (${step.description})`);
            
            const startTime = Date.now();
            const response = await axios.post(`${API_BASE}/chat`, {
                message: step.message,
                context: context
            });
            const endTime = Date.now();
            
            context = response.data.context;
            const duration = endTime - startTime;
            
            console.log(`   ✅ Response in ${duration}ms`);
            
            // Show response snippet
            const responseSnippet = response.data.response.substring(0, 50);
            console.log(`   🤖 "${responseSnippet}..."`);
            
        } catch (error) {
            console.log(`   ❌ Error: ${error.message}`);
        }
    }
    
    // Test flight search flow
    console.log('\n📋 Flight Search Flow:');
    console.log('-'.repeat(40));
    
    try {
        console.log('   💬 "price" (Preference selection - triggers search)');
        
        const startTime = Date.now();
        const response = await axios.post(`${API_BASE}/chat`, {
            message: "price",
            context: context
        });
        const endTime = Date.now();
        
        const duration = endTime - startTime;
        console.log(`   ✅ Flight search completed in ${duration}ms`);
        
        // Show flight results snippet
        const responseSnippet = response.data.response.substring(0, 100);
        console.log(`   🛫 "${responseSnippet}..."`);
        
    } catch (error) {
        console.log(`   ❌ Error: ${error.message}`);
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log('🎯 Loading UX Features:');
    console.log('✅ Context-aware loading indicators');
    console.log('✅ Animated search progress messages');
    console.log('✅ Spinning loader animations');
    console.log('✅ Button loading states');
    console.log('✅ Automatic cleanup of intervals');
    console.log('✅ Smooth user experience');
    
    console.log('\n💡 Loading Indicator Types:');
    console.log('• Typing Indicator: Simple text with subtle animation');
    console.log('• Searching Indicator: Gradient background with rotating messages');
    console.log('• Button Loader: Spinning icon in send button');
    console.log('• Auto-hide: All indicators disappear when results arrive');
    
    console.log('\n🌐 Open index.html to see the full loading experience!');
    console.log('   Try: "search flights" → "Delhi" → "Mumbai" → "tomorrow" → "price"');
}

// Run the demonstration
demonstrateLoadingUX().catch(console.error);

