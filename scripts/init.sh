#!/bin/bash
echo "🔧 Initializing Data Engineering Environment..."
mkdir -p projects/datamart-intelligence-platform/{dags,dbt/{models,tests},scripts,streamlit,init-scripts}
mkdir -p config
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env from template"
fi
echo "🎉 Initialization complete!"