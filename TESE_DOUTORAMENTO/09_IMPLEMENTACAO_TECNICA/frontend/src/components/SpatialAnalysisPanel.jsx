import React, { useState } from 'react'
import { 
  MapIcon, 
  ArrowDownTrayIcon, 
  GlobeAltIcon,
  DocumentTextIcon,
  CogIcon
} from '@heroicons/react/24/outline'

export default function SpatialAnalysisPanel({ analysisId }) {
  const [generating, setGenerating] = useState(false)
  const [spatialData, setSpatialData] = useState(null)
  const [downloadUrl, setDownloadUrl] = useState(null)
  const [interpretation, setInterpretation] = useState(null)

  const generateShapefiles = async () => {
    try {
      setGenerating(true)
      
      const response = await fetch(`/api/spatial-analysis/generate-shapefiles/${analysisId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_id: analysisId,
          include_players: true,
          include_pressure_zones: true,
          include_formation_lines: true,
          include_tactical_zones: true,
          output_format: "shapefile"
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setSpatialData(result)
        setDownloadUrl(result.download_url)
      } else {
        throw new Error('Failed to generate shapefiles')
      }
    } catch (error) {
      console.error('Error generating shapefiles:', error)
    } finally {
      setGenerating(false)
    }
  }

  const loadSpatialInterpretation = async () => {
    try {
      const response = await fetch(`/api/spatial-analysis/spatial-interpretation/${analysisId}`)
      if (response.ok) {
        const result = await response.json()
        setInterpretation(result.spatial_interpretation)
      }
    } catch (error) {
      console.error('Error loading spatial interpretation:', error)
    }
  }

  const downloadShapefiles = () => {
    if (downloadUrl) {
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `tactical_analysis_${analysisId.substring(0, 8)}.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
        <MapIcon className="h-5 w-5 mr-2 text-blue-600" />
        Shapefile & Spatial Analysis
      </h4>
      
      <div className="space-y-4">
        {/* Generation Controls */}
        <div className="flex space-x-3">
          <button
            onClick={generateShapefiles}
            disabled={generating}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <GlobeAltIcon className="h-4 w-4" />
                <span>Generate Shapefiles</span>
              </>
            )}
          </button>
          
          <button
            onClick={loadSpatialInterpretation}
            className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            <DocumentTextIcon className="h-4 w-4" />
            <span>Load Interpretation</span>
          </button>
        </div>

        {/* Download Section */}
        {spatialData && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h5 className="font-medium text-green-800 mb-2">Shapefiles Generated Successfully</h5>
            <p className="text-sm text-green-700 mb-3">
              Generated {Object.keys(spatialData.files_generated || {}).length} spatial data layers
            </p>
            
            <div className="grid grid-cols-2 gap-2 text-xs text-green-600 mb-3">
              {Object.entries(spatialData.files_generated || {}).map(([type, path]) => (
                <div key={type} className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  <span className="capitalize">{type.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
            
            <button
              onClick={downloadShapefiles}
              className="flex items-center space-x-2 bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700"
            >
              <ArrowDownTrayIcon className="h-4 w-4" />
              <span>Download ZIP</span>
            </button>
          </div>
        )}

        {/* Spatial Interpretation */}
        {interpretation && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h5 className="font-medium text-blue-800 mb-3">Spatial Analysis Interpretation</h5>
            
            {/* Spatial Analysis Summary */}
            {interpretation.spatial_analysis && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-blue-700 mb-2">Player Distribution Analysis</h6>
                <div className="text-xs text-blue-600 space-y-1">
                  <p>• Field coverage analysis across tactical zones</p>
                  <p>• Pressure zone mapping with 10m radius around ball</p>
                  <p>• Spatial clustering and balance measurements</p>
                </div>
              </div>
            )}

            {/* Geometric Features */}
            {interpretation.geometric_features && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-blue-700 mb-2">Geometric Features</h6>
                <div className="text-xs text-blue-600 space-y-1">
                  <p>• <strong>Defensive Line:</strong> Linear formation geometry</p>
                  <p>• <strong>Team Hull:</strong> Minimum area containing all players</p>
                  <p>• <strong>Pressure Zones:</strong> Circular influence areas</p>
                </div>
              </div>
            )}

            {/* Tactical Zones */}
            {interpretation.tactical_zones && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-blue-700 mb-2">Tactical Zone Analysis</h6>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="bg-white p-2 rounded border">
                    <p className="font-medium text-blue-800">Defensive Third</p>
                    <p className="text-blue-600">0-35m zone</p>
                  </div>
                  <div className="bg-white p-2 rounded border">
                    <p className="font-medium text-blue-800">Middle Third</p>
                    <p className="text-blue-600">35-70m zone</p>
                  </div>
                  <div className="bg-white p-2 rounded border">
                    <p className="font-medium text-blue-800">Attacking Third</p>
                    <p className="text-blue-600">70-105m zone</p>
                  </div>
                </div>
              </div>
            )}

            {/* Spatial Relationships */}
            {interpretation.spatial_relationships && (
              <div>
                <h6 className="text-sm font-medium text-blue-700 mb-2">Spatial Relationships</h6>
                <div className="text-xs text-blue-600 space-y-1">
                  <p>• <strong>Distance Analysis:</strong> Player-to-player and player-to-ball measurements</p>
                  <p>• <strong>Coverage Analysis:</strong> Voronoi diagrams for field responsibility</p>
                  <p>• <strong>Influence Zones:</strong> Areas of effective player intervention</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* GIS Information */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h5 className="font-medium text-gray-800 mb-2 flex items-center">
            <CogIcon className="h-4 w-4 mr-2" />
            GIS Technical Information
          </h5>
          
          <div className="text-xs text-gray-600 space-y-2">
            <div>
              <p className="font-medium">Coordinate System:</p>
              <p>Local field coordinates (105m × 68m)</p>
            </div>
            
            <div>
              <p className="font-medium">Generated Layers:</p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                <li><strong>Player Positions:</strong> Point features with attributes</li>
                <li><strong>Pressure Zones:</strong> Circular polygons around ball/players</li>
                <li><strong>Formation Lines:</strong> LineString connecting players by role</li>
                <li><strong>Tactical Zones:</strong> Field thirds and corridor polygons</li>
              </ul>
            </div>
            
            <div>
              <p className="font-medium">Compatible Software:</p>
              <p>QGIS, ArcGIS, PostGIS, GeoPandas, Leaflet</p>
            </div>
            
            <div>
              <p className="font-medium">Analysis Capabilities:</p>
              <p>Distance calculations, area coverage, spatial clustering, proximity analysis</p>
            </div>
          </div>
        </div>

        {/* Usage Instructions */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h5 className="font-medium text-yellow-800 mb-2">How to Use Shapefiles</h5>
          <div className="text-xs text-yellow-700 space-y-1">
            <p>1. <strong>Download:</strong> Click "Download ZIP" to get all spatial files</p>
            <p>2. <strong>Extract:</strong> Unzip the downloaded file to access .shp, .dbf, .shx files</p>
            <p>3. <strong>Import:</strong> Load into GIS software (QGIS recommended for free option)</p>
            <p>4. <strong>Analyze:</strong> Perform spatial analysis, create maps, measure distances</p>
            <p>5. <strong>Visualize:</strong> Create tactical maps with custom symbology and labels</p>
          </div>
        </div>
      </div>
    </div>
  )
}
