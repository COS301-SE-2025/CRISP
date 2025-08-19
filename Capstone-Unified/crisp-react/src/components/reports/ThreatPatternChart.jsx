import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const ThreatPatternChart = ({ threatPatterns, title = "Threat Patterns Distribution", width, height }) => {
  const svgRef = useRef();
  const containerRef = useRef();

  useEffect(() => {
    if (!threatPatterns || (!threatPatterns.indicator_type_distribution && !threatPatterns.tactic_distribution)) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll("*").remove();

    // Get responsive dimensions
    const container = containerRef.current;
    const containerWidth = width || (container ? container.offsetWidth : 600);
    const containerHeight = height || 400;

    // Determine which data to use (prefer indicator types, fallback to tactics)
    let data = [];
    let chartTitle = title;
    
    if (threatPatterns.indicator_type_distribution && Object.keys(threatPatterns.indicator_type_distribution).length > 0) {
      data = Object.entries(threatPatterns.indicator_type_distribution)
        .map(([key, value]) => ({ 
          label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()), 
          value: value, 
          type: 'indicator' 
        }))
        .sort((a, b) => b.value - a.value);
      chartTitle = "IoC Type Distribution";
    } else if (threatPatterns.tactic_distribution && Object.keys(threatPatterns.tactic_distribution).length > 0) {
      data = Object.entries(threatPatterns.tactic_distribution)
        .map(([key, value]) => ({ 
          label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()), 
          value: value, 
          type: 'tactic' 
        }))
        .sort((a, b) => b.value - a.value);
      chartTitle = "TTP Tactic Distribution";
    }

    if (data.length === 0) return;

    // Set up dimensions and margins
    const margin = { top: 60, right: 20, bottom: 80, left: 60 };
    const innerWidth = containerWidth - margin.left - margin.right;
    const innerHeight = containerHeight - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr("width", containerWidth)
      .attr("height", containerHeight);

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Set up scales
    const xScale = d3.scaleBand()
      .domain(data.map(d => d.label))
      .range([0, innerWidth])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .nice()
      .range([innerHeight, 0]);

    // Color scale
    const colorScale = d3.scaleOrdinal()
      .domain(data.map(d => d.label))
      .range(['#ff6b6b', '#4ecdc4', '#45b7d1', '#f7b731', '#5f27cd', '#fd79a8', '#00b894', '#e17055', '#74b9ff', '#a29bfe']);

    // Create tooltip
    const tooltip = d3.select("body").append("div")
      .attr("class", "d3-tooltip-pattern")
      .style("opacity", 0)
      .style("position", "absolute")
      .style("background", "rgba(0, 0, 0, 0.8)")
      .style("color", "white")
      .style("padding", "8px")
      .style("border-radius", "4px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("z-index", "1000");

    // Add bars
    g.selectAll(".bar")
      .data(data)
      .enter().append("rect")
      .attr("class", "bar")
      .attr("x", d => xScale(d.label))
      .attr("width", xScale.bandwidth())
      .attr("y", d => yScale(d.value))
      .attr("height", d => innerHeight - yScale(d.value))
      .attr("fill", d => colorScale(d.label))
      .attr("opacity", 0.8)
      .style("cursor", "pointer")
      .on("mouseover", function(event, d) {
        tooltip.transition()
          .duration(200)
          .style("opacity", .9);
        tooltip.html(`
          <strong>${d.label}</strong><br/>
          Count: ${d.value}<br/>
          Percentage: ${((d.value / data.reduce((sum, item) => sum + item.value, 0)) * 100).toFixed(1)}%
        `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");
        
        d3.select(this)
          .transition()
          .duration(100)
          .attr("opacity", 1);
      })
      .on("mouseout", function() {
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
        
        d3.select(this)
          .transition()
          .duration(100)
          .attr("opacity", 0.8);
      });

    // Add value labels on bars
    g.selectAll(".bar-label")
      .data(data)
      .enter().append("text")
      .attr("class", "bar-label")
      .attr("x", d => xScale(d.label) + xScale.bandwidth() / 2)
      .attr("y", d => yScale(d.value) - 5)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("font-weight", "500")
      .style("fill", "#333")
      .text(d => d.value);

    // Add X axis
    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))
      .selectAll("text")
      .style("font-size", "11px")
      .style("fill", "#666")
      .attr("transform", "rotate(-45)")
      .style("text-anchor", "end");

    // Add Y axis
    g.append("g")
      .call(d3.axisLeft(yScale)
        .ticks(6))
      .selectAll("text")
      .style("font-size", "12px")
      .style("fill", "#666");

    // Add axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (innerHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#666")
      .text("Count");

    // Add title
    g.append("text")
      .attr("x", innerWidth / 2)
      .attr("y", 0 - (margin.top / 2))
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "600")
      .style("fill", "#333")
      .text(chartTitle);

    // Add grid lines
    g.append("g")
      .attr("class", "grid")
      .call(d3.axisLeft(yScale)
        .tickSize(-innerWidth)
        .tickFormat("")
      )
      .style("stroke-dasharray", "3,3")
      .style("opacity", 0.3);

    // Cleanup function
    return () => {
      tooltip.remove();
    };

  }, [threatPatterns, title, width, height]);

  return (
    <div ref={containerRef} className="threat-pattern-chart" style={{ width: '100%', overflowX: 'auto' }}>
      <svg ref={svgRef}></svg>
      <style>{`
        .threat-pattern-chart {
          background: white;
          border-radius: 8px;
          padding: 16px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          margin: 16px 0;
        }
        
        .threat-pattern-chart svg {
          display: block;
          margin: 0 auto;
        }
        
        :global(.d3-tooltip-pattern) {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        :global(.grid line) {
          stroke: #ddd;
        }
        
        :global(.grid path) {
          stroke-width: 0;
        }
        
        .threat-pattern-chart :global(.domain) {
          stroke: #ccc;
        }
        
        .threat-pattern-chart :global(.tick line) {
          stroke: #ccc;
        }
      `}</style>
    </div>
  );
};

export default ThreatPatternChart;