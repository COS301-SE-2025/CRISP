import React from 'react';

const Reports = () => {
  return (
    <div className="reports-page">
      <h1>Reports</h1>
      <p>Generate and view various threat intelligence reports.</p>
      
      <div className="placeholder-content">
        <div className="content-box">
          <h2>Report Generation</h2>
          <p>This section will contain functionality for generating and managing various types of threat intelligence reports.</p>
          
          <div className="feature-list">
            <div className="feature-item">
              <h3>Threat Intelligence Summary</h3>
              <p>Generate comprehensive threat intelligence reports</p>
            </div>
            
            <div className="feature-item">
              <h3>TTP Analysis Report</h3>
              <p>Detailed analysis of tactics, techniques, and procedures</p>
            </div>
            
            <div className="feature-item">
              <h3>Trust Relationship Reports</h3>
              <p>Reports on organizational trust metrics</p>
            </div>
            
            <div className="feature-item">
              <h3>STIX/TAXII Feed Reports</h3>
              <p>Analysis of threat intelligence feeds</p>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .reports-page {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .reports-page h1 {
          color: #2c3e50;
          margin-bottom: 20px;
        }

        .placeholder-content {
          margin-top: 30px;
        }

        .content-box {
          background: white;
          border-radius: 8px;
          padding: 30px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          border-left: 4px solid #e74c3c;
        }

        .content-box h2 {
          color: #2c3e50;
          margin-bottom: 15px;
        }

        .content-box p {
          color: #7f8c8d;
          line-height: 1.6;
          margin-bottom: 20px;
        }

        .feature-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .feature-item {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 6px;
          border-left: 3px solid #e74c3c;
        }

        .feature-item h3 {
          color: #2c3e50;
          margin-bottom: 10px;
          font-size: 16px;
        }

        .feature-item p {
          color: #6c757d;
          margin: 0;
          font-size: 14px;
        }
      `}</style>
    </div>
  );
};

export default Reports;