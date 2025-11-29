import { useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';

interface GraphProps {
    elements: {
        nodes: any[];
        edges: any[];
    };
    layout?: string;
    onNodeClick?: (nodeData: any) => void;
    onCy?: (cy: cytoscape.Core) => void;
}

export default function Graph({ elements, layout = 'cose', onNodeClick, onCy }: GraphProps) {
    const cyRef = useRef<cytoscape.Core | null>(null);

    const cyElements = [
        ...elements.nodes,
        ...elements.edges
    ];

    const style = [
        {
            selector: 'node',
            style: {
                'background-color': 'data(color)',
                'label': 'data(label)',
                // Tamanho dinâmico baseado em total_mensagens
                'width': (ele: any) => {
                    const total = ele.data('total_mensagens') || 0;
                    // Tamanho mínimo 50, máximo 100, proporcional a log(mensagens)
                    if (total === 0) return 50;
                    const size = 50 + Math.min(50, Math.log(total + 1) * 15);
                    return size;
                },
                'height': (ele: any) => {
                    const total = ele.data('total_mensagens') || 0;
                    if (total === 0) return 50;
                    const size = 50 + Math.min(50, Math.log(total + 1) * 15);
                    return size;
                },
                'font-size': '11px',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'color': '#fff',
                'text-outline-width': 2,
                'text-outline-color': '#000',
                'text-margin-y': 8,
                'shape': 'ellipse',
                'border-width': 2,
                'border-color': '#000',
                'border-opacity': 0.3,
            } as any
        },
        {
            selector: 'node[foto]',
            style: {
                'background-image': 'data(foto)',
                'background-fit': 'cover',
                'border-width': 3,
                'border-color': 'data(color)'
            }
        },
        {
            selector: 'node[type = "IP"]',
            style: {
                'shape': 'rectangle',
                'width': 60,
                'height': 40
            }
        },

        {
            selector: 'node[is_target = true]',
            style: {
                'border-width': 0, // Remove borda amarela
            }
        },
        {
            selector: 'edge',
            style: {
                'label': (ele: any) => {
                    const weight = ele.data('weight') || 0;
                    return weight > 0 ? weight : '';
                },
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'target-arrow-color': '#94a3b8',
                'line-color': '#94a3b8',
                'opacity': 0.8,
                'width': (ele: any) => {
                    const weight = ele.data('weight') || 1;
                    return Math.min(4, 1 + Math.log(weight + 1));
                },
                'text-rotation': 'autorotate',
                'text-margin-y': -10,
                'text-background-opacity': 1,
                'text-background-color': '#ffffff',
                'text-background-padding': 2,
                'text-background-shape': 'round-rectangle',
                'font-size': '10px',
                'color': '#475569'
            } as any
        },
        {
            selector: 'node:selected',
            style: {
                'border-width': 4,
                'border-color': '#3b82f6', // Azul para seleção
                'border-opacity': 1
            }
        },
        {
            selector: '.highlighted',
            style: {
                'background-color': '#3b82f6',
                'line-color': '#3b82f6',
                'target-arrow-color': '#3b82f6',
                'transition-property': 'background-color, line-color, target-arrow-color',
                'transition-duration': 100
            } as any
        }
    ];

    // Highlight connections on hover
    useEffect(() => {
        if (cyRef.current) {
            const cy = cyRef.current;

            cy.on('mouseover', 'node', (evt) => {
                const node = evt.target;
                // Destacar conexões diretas
                node.neighborhood().addClass('highlighted');
                node.addClass('highlighted');
            });

            cy.on('mouseout', 'node', (evt) => {
                const node = evt.target;
                node.neighborhood().removeClass('highlighted');
                node.removeClass('highlighted');
            });
        }
    }, []);

    useEffect(() => {
        if (cyRef.current) {
            const cy = cyRef.current;

            // Limpar listeners antigos
            cy.off('tap');
            cy.off('dbltap');

            cy.on('dbltap', 'node', (evt) => {
                const node = evt.target;
                if (onNodeClick) {
                    onNodeClick(node.data());
                }
            });
        }
    }, [onNodeClick]);

    useEffect(() => {
        if (cyRef.current) {
            const cy = cyRef.current;
            // Configuração de layout mais espaçada
            const layoutConfig: any = {
                name: layout,
                animate: true,
                animationDuration: 500,
                // Aumentar espaçamento
                nodeRepulsion: 8000,
                idealEdgeLength: 150,
                nodeOverlap: 80,
                padding: 50
            };
            cy.layout(layoutConfig).run();
        }
    }, [layout, elements]);

    return (
        <div className="border rounded-lg overflow-hidden h-full bg-white dark:bg-slate-900">
            <CytoscapeComponent
                elements={cyElements}
                style={{ width: '100%', height: '100%' }}
                stylesheet={style}
                wheelSensitivity={0.2}
                cy={(cy: any) => {
                    cyRef.current = cy;
                    if (onCy) onCy(cy);
                }}
            />
        </div>
    );
}
