# 🚀 Running PACE - Project Analysis & Construction Estimating

This guide provides step-by-step instructions for setting up and running the PACE construction bidding automation platform.

<div align="center">

![PACE Logo](https://img.shields.io/badge/PACE-Intelligent%20Construction%20Estimating-blue?style=for-the-badge&logo=construction)
![Powered by Squires Lumber](https://img.shields.io/badge/Powered%20by-Squires%20Lumber-orange?style=for-the-badge)

**Intelligent Construction Estimating Platform**  
*Powered by Squires Lumber*

</div>

---

## 🏆 Professional Construction Estimating Platform

PACE - Project Analysis & Construction Estimating is designed to revolutionize how construction companies approach project bidding by providing:

- **🏆 Competitive Advantage**: Advanced bidding strategies for construction projects
- **🏛️ Multi-Agency Support**: DOT, municipal, federal, and commercial projects  
- **📊 Professional Estimating**: Industry-leading accuracy for all project types

### 🏗️ Market Segments Supported

| Segment | Description | Examples |
|---------|-------------|----------|
| **DOT & Highway Projects** | State transportation departments | CalTrans, TxDOT, FDOT |
| **Municipal Construction** | City and county infrastructure | Water treatment, roads, buildings |
| **Federal Infrastructure** | Government construction projects | Courthouses, military facilities |
| **Commercial Construction** | Private sector development | Office complexes, retail centers |
| **Industrial Projects** | Manufacturing and processing | Factories, warehouses, refineries |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

### Automated Setup

**macOS/Linux:**
```bash
# Clone and run
git clone https://github.com/your-org/pace-construction-estimating.git
cd pace-construction-estimating
chmod +x run_app.sh
./run_app.sh
```

**Windows:**
```cmd
# Clone and run
git clone https://github.com/your-org/pace-construction-estimating.git
cd pace-construction-estimating
run_app.bat
```

The scripts will automatically:
- ✅ Check Python version compatibility
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Set up data directories
- ✅ Launch the application

---

## 🛠️ Manual Installation

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Verify installation
python -c "import streamlit; print('✅ Installation successful!')"
```

### Step 3: Create Directories

```bash
# Create necessary directories
mkdir -p data/{uploads,cache,backups,temp}
mkdir -p output/{bids,catalogs,reports,analyses}
mkdir -p logs
```

### Step 4: Launch Application

```bash
# Run the application
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🌐 Accessing the Application

Once launched, access PACE at:
- **Local**: http://localhost:8501
- **Network**: http://your-ip:8501

---

## 🏗️ Application Features

### 📊 Dashboard
- **Professional Overview**: Real-time system status and metrics
- **Market Segments**: Visual representation of supported project types
- **Success Metrics**: Competitive advantage, multi-agency support, professional estimating
- **Quick Actions**: Direct access to key features

### 📋 Catalog Extraction
- **Multi-format Support**: Whitecap and other supplier catalogs
- **Automated Processing**: Intelligent product data extraction
- **Real-time Validation**: Quality checks and error handling
- **Export Options**: Excel, JSON, and email formats

### 🔍 Project Analysis
- **Multi-agency Support**: CalTrans, DOT, municipal, federal, commercial
- **Intelligent Recognition**: Project-specific terminology and requirements
- **Quantity Extraction**: Automated material and equipment identification
- **Professional Reports**: Detailed analysis with actionable insights

### 💰 Bid Generation
- **Agency-specific Templates**: CalTrans, DOT, municipal, federal, commercial
- **Automated Pricing**: Markup calculations, taxes, waste factors
- **Competitive Analysis**: Market-based pricing strategies
- **Professional Export**: Excel, PDF, and agency-specific formats

### ⚙️ Settings & Configuration
- **System Configuration**: Database, logging, and performance settings
- **Agency Support**: Multi-agency configurations and requirements
- **Data Management**: Backup, restore, and maintenance tools
- **Email Integration**: SMTP settings and notification preferences

---

## 🔧 Configuration

### Environment Variables

```bash
# Database configuration
PACE_DB_PATH=data/pace_construction.db

# Logging configuration  
PACE_LOG_LEVEL=INFO

# Agency-specific settings
PACE_DEFAULT_AGENCY=caltrans

# Performance settings
PACE_MAX_FILE_SIZE=200MB
PACE_BATCH_SIZE=100
```

### Supported Agencies

PACE includes specialized configurations for:

- **CalTrans**: California Department of Transportation standards
- **DOT Agencies**: State transportation departments (TxDOT, FDOT, NYSDOT, etc.)
- **Municipal**: City and county construction requirements
- **Federal**: Government construction specifications
- **Commercial**: Private sector development standards
- **Industrial**: Manufacturing and processing facilities

---

## 🚨 Troubleshooting

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version  # Should be 3.8+

# If using Python 3, try:
python3 --version
python3 -m pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Find process using port 8501
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Kill process or use different port
streamlit run main.py --server.port 8502
```

#### Permission Issues
```bash
# Fix script permissions
chmod +x run_app.sh

# Run with sudo if needed (not recommended)
sudo ./run_app.sh
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Performance Optimization

- **Memory**: Increase system RAM to 8GB+ for large projects
- **Storage**: Use SSD for faster file processing
- **Network**: Ensure stable internet for catalog updates
- **Browser**: Use Chrome or Firefox for best performance

---

## 📞 Support

### Getting Help

- **Documentation**: [PACE Wiki](https://github.com/your-org/pace-construction-estimating/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/pace-construction-estimating/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/pace-construction-estimating/discussions)
- **Email**: support@pace-construction.com

### Professional Support

For enterprise customers and professional support:
- **Phone**: 1-800-PACE-SUP
- **Email**: enterprise@pace-construction.com
- **Hours**: Monday-Friday, 8AM-6PM PST

---

## 🔄 Updates

### Automatic Updates
```bash
# Update to latest version
git pull origin main
pip install -r requirements.txt --upgrade
```

### Version Information
- **Current Version**: 1.0.0
- **Last Updated**: January 2024
- **Python Support**: 3.8+
- **Streamlit Version**: 1.28+

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**PACE - Project Analysis & Construction Estimating**  
*Intelligent Construction Estimating Platform*  
**Powered by Squires Lumber**

[Website](https://pace-construction.com) • [Documentation](https://docs.pace-construction.com) • [Support](mailto:support@pace-construction.com)

</div> 